import asyncio

from sanic import Blueprint

import ujson

from . import event

bp = Blueprint('ws_location')

event.discover()


@bp.websocket('/stream')
async def channel(request, ws):
    await asyncio.gather(listeners(request, ws), *publishers(request, ws))


async def listeners(request, ws):
    while True:
        try:
            message = ujson.loads(await ws.recv())
        except ValueError:
            continue
        handler = event.get_listener(message['type'])
        if handler:
            await handler(request, message['data'])


def publishers(request, ws):
    return [publisher(request, ws) for publisher in event.get_publishers()]
