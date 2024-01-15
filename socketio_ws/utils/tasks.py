"""
Фоновые таски.
"""
from typing import List

from socketio import AsyncClient as socketio_async_client

from socketio_ws.utils.settings import MY_LOGGER, MAIN_SOCKET_SERVER_URL


async def send_notifications_bg_task(sio: socketio_async_client, message: str, sids_lst: List[str]):
    """
    Фоновая таска для отправки уведомлений.
    """
    MY_LOGGER.debug(f'Отправляем событие веб-сокет серверу {MAIN_SOCKET_SERVER_URL!r} на отправку уведомлений. | '
                    f'Текст:{message} | список SID: {sids_lst}')
    await sio.emit(event='send_notifications', data={"message": message, "sids_lst": sids_lst})
