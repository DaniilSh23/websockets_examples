import jwt


async def encode_token():
    """
    Пилим JWT токен для соединения по веб-сокету. Его нужно вставить в JS код на фронте.
    """
    return jwt.encode({"user_id": 777}, "secret_key_for_encode", algorithm="HS256")


async def authenticate_user(auth_data):
    """
    Функция для аутентификации пользователя, который коннектится по веб-сокету.
    """
    payload = jwt.decode(auth_data.get("token"), "secret_key_for_encode", algorithms=["HS256"])
    return payload.get("user_id")
