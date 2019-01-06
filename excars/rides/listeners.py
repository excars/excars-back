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
    await repositories.UserLocationRepository(redis_cli).save(user.uid, location)


@event.listen(constants.MessageType.SOCKET_CLOSE)
async def on_close(request, ws, payload, user):
    del ws, payload
    redis_cli = request.app.redis

    profile_repo = repositories.ProfileRepository(redis_cli)
    profile = await profile_repo.get(user.uid)

    coros = [profile_repo.expire(user.uid)]
    if profile:
        coros.append(repositories.RideRepository(redis_cli).expire(profile))

    await asyncio.gather(*coros)


@event.listen(constants.MessageType.SOCKET_OPEN)
async def on_open(request, ws, payload, user):
    del ws, payload
    redis_cli = request.app.redis
    await asyncio.gather(
        repositories.ProfileRepository(redis_cli).persist(user.uid),
        repositories.RideRepository(redis_cli).persist(user.uid),
    )
