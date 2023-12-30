"""Асинхронный клиент для socketio."""


import asyncio
import socketio


# Создается объект клиента sio для работы с событиями веб-сокета.
sio = socketio.AsyncClient()


@sio.event
async def connect():
    """
    Вызывается при успешном подключении к серверу. Выводит сообщение об успешном подключении.
    """
    print('connection established')


@sio.event
async def my_message(data):
    """
    Вызывается при получении сообщения от сервера.
    Выводит содержимое полученного сообщения и отправляет ответное сообщение серверу.
    """
    print('message received with: ', data)
    await sio.emit('my response', {'response': 'client response'})


@sio.event
async def disconnect():
    """
    Вызывается при отключении от сервера. Выводит сообщение о разрыве соединения.
    """
    print('disconnected from server')


async def send_message(text: str):
    """
    Функция для отправки сообщения серверу веб-сокета.
    """
    await sio.emit(event='chat_message', data=text)


async def main():
    await sio.connect('http://localhost:8080')
    await send_message(text='что делал слон, когда пришел НаПолеОн?')
    await sio.wait()    # Используется для блокировки основного потока выполнения программы и ожидания событий


if __name__ == '__main__':
    asyncio.run(main())
