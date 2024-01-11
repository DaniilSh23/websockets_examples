# WebSockets examples
### Репа, в которой я пробую разные варианты питонячей реализации веб-сокетов.

## Что тут есть полезного?
- В директории `socketio_ws` лежат файлы для реализации клиентов и сервера на socket.io. 
  * В `ws_server.py` находится базовый пример кода веб-сокет сервера на python. 
  * В `static/socket_io_client.html` представлена простейшая реализация браузерного клиента веб-сокет на JS. Это, по сути своей, html страничка, на которой мы можем что-то написать и посмотреть, что нам ответит сервер. 
  * В `ws_async_client.py` лежит базовый пример асинхронной реализации клиента на python.
- В файле `env` лежат необходимые переменные окружения
  * AI_WEBAPP_URL - URL адрес, на котором развернуто веб-приложения для работы с OpenAI
  * AI_WEBAPP_TOKEN - Токен для взаимодействия с веб-приложением по урлу `AI_WEBAPP_URL`
  * OPENAI_API_KEY - Токен для работы с OpenAI напрямую

OpenAI не обрабатывает запросы с РФ айпи адресов, поэтому у меня была необходимость развернуть свое веб-приложение на сервере в другой стране и использовать API OpenAI.

## Что с этим делать?
- Запускаем веб-приложение
- Переходим по адресу `/ws-page`
- В открывшейся веб-странице можно:
  * Отправить сообщение на сервер по веб-сокету и получить ответ
  * Отправить сообщение на сервер для генерации ответа моделью AI. Сообщение будет обработано через сторонее веб-приложение. (нужно внести в `.env` файл `AI_WEBAPP_URL` и `AI_WEBAPP_TOKEN`)
  * Отправить сообщение на сервер для генерации ответа моделью AI напрямую (нужно внести в `.env` файл `OPENAI_API_KEY` )