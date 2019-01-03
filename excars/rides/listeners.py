import asyncio

from excars.ws import event

from . import constants, factories, repositories, schemas


@event.listen(constants.MessageType.LOCATION)
async def receive_location(request, ws, payload, user):
    del ws

    data, errors = schemas.WSLocationPayload().load(payload)
    if errors:
        return

    location = factories.make_user_location(user, **data)

    redis_cli = request.app.redis
    await repositories.UserLocationRepository(redis_cli).save(str(user.uid), location)


@event.listen(constants.MessageType.SOCKET_CLOSE)
async def on_close(request, ws, payload, user):
    del ws, payload

    redis_cli = request.app.redis
    await asyncio.gather(
        repositories.UserLocationRepository(redis_cli).expire(str(user.uid)),
        repositories.ProfileRepository(redis_cli).expire(str(user.uid)),
    )


@event.listen(constants.MessageType.SOCKET_OPEN)
async def on_open(request, ws, payload, user):
    del ws, payload
    redis_cli = request.app.redis
    await asyncio.gather(
        repositories.UserLocationRepository(redis_cli).unexpire(str(user.uid)),
        repositories.ProfileRepository(redis_cli).save(factories.make_profile(user))
    )
