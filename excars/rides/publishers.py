# pylint: skip-file

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

        profile_repo = repositories.ProfileRepository(redis_cli)

        ride_repo = repositories.RideRepository(redis_cli)
        user_ride_uid = await ride_repo.get_ride_uid(user.uid)

        map_items = []
        for location in locations:
            if location.user_uid == str(user.uid):
                continue

            profile = await profile_repo.get(location.user_uid)
            if not profile:
                continue

            ride_uid = await ride_repo.get_ride_uid(profile.uid)
            if ride_uid and ride_uid != user_ride_uid:
                continue

            has_same_ride = bool(user_ride_uid and (user_ride_uid == ride_uid))
            map_items.append(factories.make_map_item(profile, location, has_same_ride))

        if not map_items:
            continue

        message = factories.make_message(
            constants.MessageType.MAP,
            payload=schemas.MapItemSchema(many=True).dump(map_items).data,
        )

        await ws.send(schemas.MessageSchema().dumps(message).data)
