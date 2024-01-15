import jwt

from my_exceptions.my_base_exceptions import AuthDataIsEmpty
from socketio_ws.utils.settings import SECRET_KEY, MY_LOGGER


async def encode_token(payload):
    """
    Пилим JWT токен для соединения по веб-сокету. Его нужно вставить в JS код на фронте.
    """
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


async def authenticate_user(auth_data):
    """
    Функция для аутентификации пользователя, который коннектится по веб-сокету.
    """
    if not auth_data:
        MY_LOGGER.warning(f'Отсутствуют данные для авторизации веб-сокет клиента!')
        raise AuthDataIsEmpty(f'Отсутствуют данные для авторизации веб-сокет клиента! | auth_data == {auth_data}')

    payload = jwt.decode(auth_data.get("token"), SECRET_KEY, algorithms=["HS256"])
    return payload.get("user_id")
