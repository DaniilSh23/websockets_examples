import random

from fastapi import FastAPI, Request, Depends
import socketio
from fastapi.responses import HTMLResponse

from socketio_ws.utils.auth import authenticate_user, encode_token
from socketio_ws.utils.project_requests import get_gpt_answer_through_my_webapp, get_gpt_answer
from socketio_ws.utils.settings import base_templates, MY_LOGGER, PROMPTS, SOCKET_ADMIN_LOGIN, SOCKET_ADMIN_PASSWORD, \
    REDIS_HOST, REDIS_PORT, REDIS_STORAGE

# Инициализируем приложуху FastApi
fs_app = FastAPI()

# Создаем менеджера редиса для socket.io
# redis_manager = socketio.AsyncRedisManager(f'redis://{REDIS_USERNAME}:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}')
redis_manager = socketio.AsyncRedisManager(f'redis://{REDIS_HOST}:{REDIS_PORT}/0')

# Создаем сервак сокетов
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins='*', client_manager=redis_manager)

# Регистрируем сервак socket.io и приложение FastAPI
ws_app = socketio.ASGIApp(sio, fs_app)

# Прикручиваем админку (она доступна по адресу: https://admin.socket.io/)
sio.instrument(auth={
    'username': SOCKET_ADMIN_LOGIN,
    'password': SOCKET_ADMIN_PASSWORD,
})


@sio.on("connect")
async def handle_connect(sid, environ, auth_data):
    """
    Socket.io обработка события коннекта.
    """
    MY_LOGGER.info(f"Client {sid} connected")
    user_id = await authenticate_user(auth_data)
    MY_LOGGER.info(f"Client user_id == {user_id}")

    # Сессия нужна, чтобы связать с SID user_id, это понадобиться, чтобы удалить данные из redis при disconnect
    await sio.save_session(sid, {'user_id': user_id})
    # В redis будем хранить user_id в качестве ключа и sid в качестве значения
    result = await REDIS_STORAGE.set(user_id, sid)
    MY_LOGGER.debug(f'Результат записи ключа в redis: {result}')


@sio.on("disconnect")
async def handle_disconnect(sid):
    """
    Socket.io обработка события дисконнекта.
    """
    MY_LOGGER.info(f"Client {sid} disconnected")
    # Удаляем данные из редиса при дисконнекте юзера
    user_session = await sio.get_session(sid)
    result = await REDIS_STORAGE.delete(user_session["user_id"])
    # result = await redis_client.delete(user_session["user_id"])
    MY_LOGGER.debug(f'Результат удаления ключа из redis: {result}')


@sio.on("client_event")
async def handle_client_event(sid, data):
    """
    Socket.io обработка получения события от клиента
    """
    session = await sio.get_session(sid)
    MY_LOGGER.info(f"Получены данные от клиента sid=={sid}, user_id=={session['user_id']} | {data}")
    await sio.emit(event='base_server_event', data={'message': f'Все говорят: "{data}", а ты купи слона!'}, room=sid)


@sio.on("client_event_for_ai")
async def client_event_for_ai(sid, data):
    """
    Хэндлер веб-сокет событий от клиента для последующего запроса к AI модели, через сторонее веб-приложение
    и возврата ответа клиенту. Сообщение клиента должно лежать в параметре aiMessage.
    """
    # В сессию можно записывать саммаризацию диалога клиента с ИИ,
    # чтобы модель могла вести диалог в контексте разговора
    session = await sio.get_session(sid)
    MY_LOGGER.info(f"Получен event для модели AI (через сторонее веб-приложение) от клиента sid=={sid}, "
                   f"user_id=={session['user_id']} | {data}")

    # Запрос к AI моделе
    _, response_json = await get_gpt_answer_through_my_webapp(prompt=PROMPTS[random.choice(list(PROMPTS.keys()))],
                                                              query=data.get("aiMessage"))
    await sio.emit(
        event='server_ai_answer',
        data={'message': response_json.get("answer")},
        room=sid
    )


@sio.on("client_event_for_ai_right_now")
async def client_event_for_ai_right_now(sid, data):
    """
    Хэндлер веб-сокет событий от клиента для последующего запроса к AI модели напрямую и возврата ответа клиенту.
    Сообщение клиента должно лежать в параметре aiMessage.
    """
    # В сессию можно записывать саммаризацию диалога клиента с ИИ,
    # чтобы модель могла вести диалог в контексте разговора
    session = await sio.get_session(sid)
    MY_LOGGER.info(f"Получен event для модели AI (напрямую) от клиента sid=={sid}, user_id=={session['user_id']} "
                   f"| {data}")

    # Запрос к AI моделе
    success, answer = await get_gpt_answer(
        prompt=PROMPTS[random.choice(list(PROMPTS.keys()))],
        query=data.get("aiMessage"),
    )
    await sio.emit(
        event='server_ai_answer_right_now',
        data={'message': answer},
        room=sid
    )


@sio.on("send_msg_to_user_by_sid")
async def send_msg_to_user_by_sid(sid, data):
    """
    Хэндлер событий клиента для отправки сообщения другому клиенту по sid.
    """
    MY_LOGGER.info(f"Получен event от клиента sid=={sid!r} для отправки сообщения другому клиенту. | {data}")
    await sio.emit(event='message_from_user', data={'message': data.get("clientMessage")}, room=data.get("clientSid"))


@sio.on("send_notifications")
async def send_notifications(sid, data):
    """
    Хэндлер событий клиента для отправки уведомлений пользователям по списку sid.
    """
    MY_LOGGER.info(f"Получен event от клиента sid=={sid!r} для отправки уведомлений клиентам по sid. | {data}")

    # Добавляем юезров в комнату
    room_name = 'notification'
    [await sio.enter_room(i_sid, room=room_name) for i_sid in data.get("sids_lst")]
    # Отправляем уведомления
    await sio.emit(event='new_notification', data={'message': data.get("message")}, room=room_name)
    # Удаляем юезров из комнаты
    [await sio.leave_room(i_sid, room=room_name) for i_sid in data.get("sids_lst")]


@fs_app.post(
    path='/send-ws-event-by-sid'
)
async def send_web_socket_event(message: str, client_sid: str):
    """
    Шлем сообщение клиенту по его sid.
    """
    MY_LOGGER.info(f'Запрос на эндпоинт: /send-ws-event-by-sid')
    await sio.emit(event='base_server_event', data={'message': message}, room=client_sid)


@fs_app.post(
    path='/send-ws-event-for-all'
)
async def send_web_socket_event(message: str):
    """
    Шлем сообщение всем, подключенным клиентам.
    """
    MY_LOGGER.info(f'Запрос на эндпоинт: /send-ws-event-for-all')
    result = await sio.emit(event='base_server_event', data={'message': message})
    MY_LOGGER.info(f'Результат: /send-ws-event-for-all | {result!r}')


@fs_app.get(path='/ws-page', response_class=HTMLResponse)
async def render_ws_page(request: Request):
    """
    Рендерим страницу для работы с веб-сокетами
    """
    MY_LOGGER.info(f'Запрос на эндпоинт: /ws-page')
    # host = request.url.host
    # port = request.url.port
    context = {
        'jwt_token': await encode_token(payload={"user_id": random.randint(100, 500)}),
        "host_addr": f"{request.url.scheme}://{request.url.hostname}:{request.url.port}"
    }
    template = base_templates.get_template("socket_io_client.html")
    return template.render(request=request, **context)


@fs_app.get(path='/test')
async def endpoint_for_test(sid):
    """
    Тестовый эндпоинт. Пишем тут всякую хуйню и выполняем ее.
    """
    MY_LOGGER.info(f'Тестовый эндпоинт')
    result = await sio.get_session(sid=sid)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(ws_app, host="127.0.0.1", port=8080)
