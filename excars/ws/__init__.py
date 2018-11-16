import asyncio

from sanic import Blueprint

import ujson

from .publish_location import handler as publish_location
from .users_map import handler as users_map


bp = Blueprint('ws_location')

LOCATION_EVENT = 'LOCATION'
EVENTS = {
    LOCATION_EVENT: publish_location
}


@bp.websocket('/stream')
async def channel(request, ws):
    await asyncio.gather(listeners(request, ws), users_map(request, ws))


async def listeners(request, ws):
    while True:
        try:
            event = ujson.loads(await ws.recv())
        except ValueError:
            continue
        handler = EVENTS.get(event['type'])
        if handler:
            await handler(request, event['data'])
