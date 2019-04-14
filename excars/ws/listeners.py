import asyncio

import ujson as json

from excars.rides import constants

from . import event


async def init(request, ws, user):
    handler = event.get_listener(constants.MessageType.SOCKET_OPEN)
    asyncio.create_task(handler(request, ws, {}, user))
    try:
        while True:
            try:
                message = json.loads(await ws.recv())
            except ValueError:
                continue
            handler = event.get_listener(message['type'])
            if handler:
                asyncio.create_task(handler(request, ws, message['data'], user))
    finally:
        handler = event.get_listener(constants.MessageType.SOCKET_CLOSE)
        asyncio.create_task(handler(request, ws, {}, user))
