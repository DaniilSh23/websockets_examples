"""
Схемы запросов и ответов для веб-приложухи, которая дает интерфейс взаимодействия с веб-сокетами.
"""
from typing import List

from pydantic import BaseModel


class SConnectedUsersResponse(BaseModel):
    """
    Схема ответа на запрос получения пользователей, которые подключены к веб-сокет серверам.
    """
    connected_clients: List[int]


class SSendNotificationRequest(BaseModel):
    """
    Схема запроса для отправки уведомления через веб-сокет.
    """
    message: str
    users_ids: List[int]


class SSendNotificationResponse(SConnectedUsersResponse):
    """
    Схема ответа на запрос отправки уведомления через веб-сокет.
    """
    disconnected_clients: List[int]
