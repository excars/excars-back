import asyncio
import typing

from excars import settings
from excars.ws import event

from . import constants, entities, factories, repositories, schemas


@event.publisher
async def publish_map(request, ws, user):

    location_repo = repositories.UserLocationRepository(request.app.redis)
    profile_repo = repositories.ProfileRepository(request.app.redis)
    ride_repo = repositories.RideRepository(request.app.redis)

    while True:
        await asyncio.sleep(settings.PUBLISH_MAP_FREQUENCY)

        locations = await location_repo.list(user_uid=user.uid)
        map_items = await _prepare_map(user.uid, locations, profile_repo, ride_repo)

        message = factories.make_message(
            constants.MessageType.MAP,
            payload=schemas.MapItemSchema(many=True).dump(map_items).data,
        )

        await ws.send(schemas.MessageSchema().dumps(message).data)


async def _prepare_map(
        user_uid: str,
        locations: typing.List[entities.UserLocation],
        profile_repo: repositories.ProfileRepository,
        ride_repo: repositories.RideRepository,
) -> typing.List[entities.MapItem]:
    user_ride_uid = await ride_repo.get_ride_uid(user_uid)

    map_items = []
    for location in locations:
        if location.user_uid == str(user_uid):
            continue

        profile = await profile_repo.get(location.user_uid)
        if not profile:
            continue

        ride_uid = await ride_repo.get_ride_uid(profile.uid)
        if ride_uid and ride_uid != user_ride_uid:
            continue

        map_items.append(factories.make_map_item(
            profile=profile,
            location=location,
            has_same_ride=bool(user_ride_uid and (user_ride_uid == ride_uid)),
        ))

    return map_items
