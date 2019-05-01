import asyncio
import time
from typing import List

from aioredis import Redis

from excars.models.locations import Location, UserLocation


def _get_key() -> str:
    return "locations"


def _get_key_for(user_id: str) -> str:
    return f"users:{user_id}:location"


def _decode(data):
    return {k.decode(): v.decode() for k, v in data.items()}


async def list_for(redis_cli: Redis, user_id: str) -> List[UserLocation]:
    if await redis_cli.zrank(_get_key(), user_id) is None:
        return []

    geomembers = await redis_cli.georadiusbymember(_get_key(), member=user_id, radius=50, unit="km")
    locations = await asyncio.gather(
        *[redis_cli.hgetall(_get_key_for(geomember.decode())) for geomember in geomembers]
    )
    locations = [_decode(location) for location in locations]
    return [UserLocation(**location) for location in locations]


async def save_for(redis_cli: Redis, user_id: str, location: Location):
    await redis_cli.geoadd(
        _get_key(), latitude=str(location.latitude), longitude=str(location.longitude), member=str(user_id)
    )
    await redis_cli.hmset_dict(
        _get_key_for(user_id),
        user_id=user_id,
        latitude=str(location.latitude),
        longitude=str(location.longitude),
        course=str(location.course),
        ts=str(time.time()),
    )
