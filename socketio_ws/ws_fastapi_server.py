from fastapi import FastAPI
import socketio

from socketio_ws.utils.auth import authenticate_user, encode_token

fs_app = FastAPI()
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins='*')
ws_app = socketio.ASGIApp(sio, fs_app)     # Регистрируем сервак socket.io и приложение FastAPI


@fs_app.on_event("startup")
async def start_up_fs_app():
    print(f'ITS YOUR JWT TOKEN FOR WEB-SOCKET:\n{await encode_token()}')


@sio.on("connect")
async def handle_connect(sid, environ, auth_data, **kwargs):
    """
    Socket.io обработка события коннекта.
    """
    print(f"Client {sid} connected")
    user_id = await authenticate_user(auth_data)
    await sio.save_session(sid, {'user_id': user_id})
    print(f"Client user_id == {user_id}")


@sio.on("disconnect")
async def handle_disconnect(sid):
    """
    Socket.io обработка события дисконнекта.
    """
    print(f"Client {sid} disconnected")


@sio.on("client_event")
async def handle_client_event(sid, data):
    """
    Socket.io обработка получения события от клиента
    """
    session = await sio.get_session(sid)
    print(f"Получены данные от клиента sid=={sid}, user_id=={session['user_id']} | {data}")
    await sio.emit(event='server_event', data={'message': f'Все говорят: "{data}", а ты купи слона!'}, room=sid)


@fs_app.post(
    path='/send-ws-event-by-sid'
)
async def send_web_socket_event(message: str, client_sid: str):
    """
    Шлем сообщение клиенту по его sid.
    """
    await sio.emit(event='server_event', data={'message': message}, room=client_sid)


@fs_app.post(
    path='/send-ws-event-for-all'
)
async def send_web_socket_event(message: str):
    """
    Шлем сообщение всем, подключенным клиентам.
    """
    await sio.emit(event='server_event', data={'message': message})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(ws_app, host="127.0.0.1", port=8080)
