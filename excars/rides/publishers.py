import asyncio

from excars.ws import event

from . import constants, factories, repositories, schemas


@event.publisher
async def publish_map(request, ws, user):
    redis_cli = request.app.redis
    repo = repositories.UserLocationRepository(redis_cli)
    frequency = 1

    while True:
        await asyncio.sleep(frequency)

        locations = await repo.list(user_uid=user.uid)
        if not locations:
            continue

        message = factories.make_message(
            constants.MessageType.MAP,
            payload=schemas.UserLocationSchema(many=True).dump(locations).data,
        )

        await ws.send(schemas.MessageSchema().dumps(message).data)
