import jwt

from socketio_ws.utils.settings import SECRET_KEY


async def encode_token(payload):
    """
    Пилим JWT токен для соединения по веб-сокету. Его нужно вставить в JS код на фронте.
    """
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


async def authenticate_user(auth_data):
    """
    Функция для аутентификации пользователя, который коннектится по веб-сокету.
    """
    payload = jwt.decode(auth_data.get("token"), SECRET_KEY, algorithms=["HS256"])
    return payload.get("user_id")
