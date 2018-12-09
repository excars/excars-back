import asyncio

import ujson
from excars.ws import event

from . import constants, repositories

PUB_LOCATION_FREQUENCY = 1


@event.publisher
async def publish_map(request, ws, user):
    redis_cli = request.app.redis
    repo = repositories.UserLocationRepository(redis_cli)

    while True:
        await asyncio.sleep(PUB_LOCATION_FREQUENCY)

        locations = await repo.list(exclude=user.uid)
        if not locations:
            continue

        message = {
            'type': constants.MessageType.MAP,
            'data': locations
        }

        await ws.send(ujson.dumps(message))
