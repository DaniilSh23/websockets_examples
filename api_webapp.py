"""
Веб-приложуха, которая дает интерфейс работы с веб-сокетами через API.
"""
import random

import socketio
from fastapi import FastAPI
from fastapi import BackgroundTasks
from schemas.api_socket_schemas import SSendNotificationResponse, SSendNotificationRequest, SConnectedUsersResponse
from services.webapp_api_services import RedisService
from socketio_ws.utils.auth import encode_token
from socketio_ws.utils.settings import MY_LOGGER, MAIN_SOCKET_SERVER_URL
from socketio_ws.utils.tasks import send_notifications_bg_task

fs_app = FastAPI()
sio = socketio.AsyncClient()


@fs_app.on_event('startup')
async def startup():
    # Устанавливаем веб-сокет соединение с сервером
    MY_LOGGER.info(f'Подключаемся к веб-сокет серверу: {MAIN_SOCKET_SERVER_URL}')
    # Пилим рандомный токен
    token = await encode_token(payload={"user_id": "wake up Neo, the matrix has you. Follow to white rabbit."})
    await sio.connect(url=MAIN_SOCKET_SERVER_URL, auth={"token": token})


@fs_app.on_event('shutdown')
async def shutdown():
    # Закрываем веб-сокет соединение
    MY_LOGGER.info(f'Отключаемся от веб-сокет сервера.')
    await sio.disconnect()


@sio.event
async def connect():
    """
    Вызывается при успешном подключении к серверу. Выводит сообщение об успешном подключении.
    """
    MY_LOGGER.info('Веб-сокет клиент веб-приложения подключился')


@sio.event
async def disconnect():
    """
    Вызывается при отключении от сервера. Выводит сообщение о разрыве соединения.
    """
    MY_LOGGER.info('Веб-сокет клиент веб-приложения отключился')


@fs_app.post(path='/notification', response_model=SSendNotificationResponse)
async def send_notifications(request_data: SSendNotificationRequest, background_task: BackgroundTasks):
    """
    Эндпоинт для отправки уведомлений списку пользователей
    """
    MY_LOGGER.info(f"Получен запрос на эндпоинт /notification | request_data: {request_data!r}")

    sids, disconnected_users = await RedisService.get_sids_from_redis(users_ids=request_data.users_ids)
    background_task.add_task(func=send_notifications_bg_task, sio=sio, message=request_data.message, sids_lst=sids)
    response_data = {
        "connected_clients": set(request_data.users_ids) - set(disconnected_users),
        "disconnected_clients": disconnected_users,
    }
    return SSendNotificationResponse(**response_data)


@fs_app.get(path='/connected-users', response_model=SConnectedUsersResponse)
async def get_connected_users():
    """
    Эндпоинт для получения списка users_ids, которые подключены к веб-сокет серверам.
    """
    MY_LOGGER.info(f"Получен запрос на эндпоинт /connected-users")
    connected_users = await RedisService.get_connected_users_ids()
    return SConnectedUsersResponse(connected_clients=connected_users)
