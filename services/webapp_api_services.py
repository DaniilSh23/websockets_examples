from typing import List

from socketio_ws.utils.settings import REDIS_STORAGE, MY_LOGGER


class RedisService:

    @staticmethod
    async def get_sids_from_redis(users_ids: List[int]):
        """
        Получаем из редиса SID пользователей по user_id.
        Возвращаем список sids юзеров, которые подключены к веб-сокет серверам. И список user_id пользователей,
        которые не подключены.
        """
        MY_LOGGER.debug(f'Получаем из redis пользователей и их SID по следующему списку user_id: {users_ids!r}')
        sids = []
        disconnected_users = []
        for i_user in users_ids:
            user_sid = await REDIS_STORAGE.get(name=i_user)

            # Обработка в случаях, когда ключ найден или не найден
            if user_sid:
                sids.append(user_sid.decode("utf-8"))
            else:
                disconnected_users.append(i_user)
        return sids, disconnected_users

    @staticmethod
    async def get_connected_users_ids():
        """
        Получаем список users_ids, которые записаны в redis (при подключении к веб-сокету - записываем клиента в редис,
        при его отключении - удаляем, записи хранятся в формате key - user_id, val - sid)
        """
        MY_LOGGER.debug(f'Получаем из redis список подключенных к веб-сокет серверам user_id')
        keys = await REDIS_STORAGE.keys()
        return [key for key in keys if key.decode("utf-8").isdigit()]
