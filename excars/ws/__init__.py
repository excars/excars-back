import asyncio

import sanic_jwt
from sanic import Blueprint

import ujson

from . import event

bp = Blueprint('ws_location')

event.discover()


@bp.websocket('/stream')
@sanic_jwt.inject_user()
@sanic_jwt.protected()
async def channel(request, ws, user):
    await asyncio.gather(listeners(request, ws, user), *publishers(request, ws, user))


async def listeners(request, ws, user):
    while True:
        try:
            message = ujson.loads(await ws.recv())
        except ValueError:
            continue
        handler = event.get_listener(message['type'])
        if handler:
            await handler(request, message['data'], user)


def publishers(request, ws, user):
    return [publisher(request, ws, user) for publisher in event.get_publishers()]
