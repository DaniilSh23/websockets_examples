"""Код для клиента веб-сокета на aiohttp."""


import asyncio
import websockets


async def hello():
    uri = "ws://localhost:8080/ws"  # Замените на свой URI WebSocket сервера
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello, server!")
        response = await websocket.recv()
        print(f"Received from server: {response}")

asyncio.run(hello())