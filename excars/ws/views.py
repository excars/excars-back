import asyncio

import sanic_jwt
from sanic import Blueprint

from . import consumers, listeners, publishers

bp = Blueprint('ws')


@bp.websocket('/stream')
@sanic_jwt.inject_user()
@sanic_jwt.protected()
async def channel(request, ws, user):
    await asyncio.gather(
        listeners.init(request, ws, user),
        consumers.init(request, ws, user),
        *publishers.init(request, ws, user),
    )
