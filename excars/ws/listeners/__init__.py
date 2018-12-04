import ujson

from .. import event


async def init(request, ws, user):
    while True:
        try:
            message = ujson.loads(await ws.recv())
        except ValueError:
            continue
        handler = event.get_listener(message['type'])
        if handler:
            await handler(request, ws, message['data'], user)
