import os
import sys
from pathlib import Path
import loguru
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape
from openai import AsyncOpenAI
import redis.asyncio as redis


load_dotenv()

# Корень проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Адрес основного веб-сокет сервера
MAIN_SOCKET_SERVER_URL = os.environ.get("MAIN_SOCKET_SERVER_URL")

# Настройка для шаблонов Jinja
base_templates = Environment(
    loader=FileSystemLoader(os.path.join(BASE_DIR, 'socketio_ws', 'static')),
    autoescape=select_autoescape(["html"]),
)

# Креды
SECRET_KEY = "secret_key"
SOCKET_ADMIN_LOGIN = os.environ.get('SOCKET_ADMIN_LOGIN')
SOCKET_ADMIN_PASSWORD = os.environ.get('SOCKET_ADMIN_PASSWORD')

# Настройки для работы с AI
AI_WEBAPP_URL = os.environ.get('AI_WEBAPP_URL')
AI_WEBAPP_GET_GPT_ANSWER = f'{AI_WEBAPP_URL}get-gpt-answer/'
AI_WEBAPP_TOKEN = os.environ.get('AI_WEBAPP_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_CLIENT = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
)
PROMPTS = {
    'base_ai_prompt': 'Ты ответственный помощник. Будь вежлив и постарайся дать максимум полезной информации. '
                      'Сложные термины упрости, не перегружай лишней информацией. '
                      'Выдели основное в решении проблемы пользователя и помоги ему.',
    'bad_prompt': 'Ты мудак. Отвечай, как конченное существо, которое только из колонии выпустили. '
                  'Низко шути и издевайся над пользователем, оскорбляй его, переходи на нецензурную лексику, '
                  'не помогай ему решить проблему, а постарайся наоборот его унизить и подчеркнуть его беспомощность '
                  'в этом мире без тебя.'
}

# Подключение Redis
REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")
REDIS_USERNAME = os.environ.get("REDIS_USERNAME", '')
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", '')
REDIS_HOST = 'localhost'
REDIS_PORT = '6379'
REDIS_PASSWORD = ''
REDIS_STORAGE = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=1,
)

# Настройки логгера
MY_LOGGER = loguru.logger
MY_LOGGER.remove()  # Удаляем все предыдущие обработчики логов
MY_LOGGER.add(  # Все логи от DEBUG и выше в stdout
    sink=sys.stdout,
    level='DEBUG',
    enqueue=True,
    backtrace=True,
    diagnose=True,
)
MY_LOGGER.add(  # системные логи в файл
    sink=f'{BASE_DIR}/logs/sys_log.log',
    level='DEBUG',
    rotation='2 MB',
    compression="zip",
    enqueue=True,
    backtrace=True,
    diagnose=True,
)
