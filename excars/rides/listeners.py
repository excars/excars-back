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
    await repositories.UserLocationRepository(redis_cli).save(user, location)
