import asyncio

import ujson as json

from . import event


async def init(request, ws, user):
    handler = event.get_listener('_WEBSOCKET_OPEN')
    asyncio.ensure_future(handler(request, ws, {}, user))
    try:
        while True:
            try:
                message = json.loads(await ws.recv())
            except ValueError:
                continue
            handler = event.get_listener(message['type'])
            if handler:
                asyncio.ensure_future(handler(request, ws, message['data'], user))
    finally:
        handler = event.get_listener('_WEBSOCKET_CLOSE')
        asyncio.ensure_future(handler(request, ws, {}, user))
