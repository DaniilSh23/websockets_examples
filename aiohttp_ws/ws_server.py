"""Веб-сокет сервер на aiohttp."""


from aiohttp import web


async def websocket_handler(request):
    """
    Обработчик WebSocket запросов.
    При подключении клиента создается объект ws, который представляет WebSocket соединение.
    """
    # Создаем объект соединения
    ws = web.WebSocketResponse()
    # Подготавливаем соединение к работе
    await ws.prepare(request)

    # Запускаем цикл, в котором сервер ожидает сообщения от клиента
    # (цикл бесконочный, но какого хуя он бесконечный - хз. Наверное - это подкапотная реализация объекта ws).
    async for msg in ws:
        # Проверка, что пришло сообщение текстового типа (вообще, там есть и другие типы сообщений)
        if msg.type == web.WSMsgType.TEXT:
            # Условие для закрытия соединения
            if msg.data == 'close':
                await ws.close()
            # Обработка остальных сообщений
            else:
                print(f"MSG --- {msg!r}")
                print(f"TYPE OF MSG --- {type(msg)!r}")
                await ws.send_str('Hello, client!')

    return ws

ws_app = web.Application()
ws_app.router.add_get('/ws', websocket_handler)

if __name__ == '__main__':
    web.run_app(app=ws_app, host='localhost', port=8080)
