"""Пример кода сервера веб-сокета на socketio."""

from aiohttp import web
import socketio

# Создается объект сервера sio для обработки событий веб-сокета.
sio = socketio.AsyncServer(cors_allowed_origins='*')
# Создается объект приложения ws_app из aiohttp
ws_app = web.Application()
# Присоединяет объект сервера sio к объекту приложения ws_app.
sio.attach(ws_app)


async def index(request):
    """
    Serve the client-side application.
    Это обработчик для запросов к корневому URL.
    Он возвращает содержимое файла index.html, который представляет клиентскую часть приложения.
    """
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


# Это декораторы, указывающие на события WebSocket.
@sio.event
def connect(sid, environ, *args, **kwargs):
    """
    Вызывается при подключении клиента. Сообщение "connect" идентифицирует клиента по sid.
    """
    print("connect: ", sid)
    print("environ: ", environ)
    print("args: ", args)
    print("kwargs: ", kwargs)


@sio.event
async def client_event(sid, data):
    """
    Обрабатывает событие получения сообщения от клиента. Выводит содержимое сообщения в консоль.
    Затем отвечает фразой: 'Все говорять <message from client>, а ты купи слона!'
    """
    print("message from client:", data)
    # my_message - это нейминг функции в коде клиента, обернутой в декоратор @sio.event
    await sio.emit(event='my_message', data={'message': f'Все говорят: "{data}", а ты купи слона!'})


@sio.event
def disconnect(sid):
    """
    Вызывается при отключении клиента. Выводит сообщение об отключении в консоль.
    """
    print('disconnect ', sid)


# Добавляет маршрут для статических файлов в директории 'static', пока хз нафиг это надо
# ws_app.router.add_static('/static', 'static')
# Добавляет маршрут для обработки корневого URL.
ws_app.router.add_get('/', index)


if __name__ == '__main__':
    web.run_app(app=ws_app, host='localhost', port=8080)
