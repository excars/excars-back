import asyncio
import time
from typing import List

from aioredis import Redis

from excars.models.locations import Location, UserLocation

KEY = "user:locations"


def decode(data):
    return {k.decode(): v.decode() for k, v in data.items()}


async def list_for(redis_cli: Redis, user_id: str) -> List[UserLocation]:
    if await redis_cli.zrank(KEY, user_id) is None:
        return []

    geomembers = await redis_cli.georadiusbymember(KEY, member=user_id, radius=50, unit="km")
    locations = await asyncio.gather(
        *[redis_cli.hgetall(f"user:{geomember.decode()}:location") for geomember in geomembers]
    )
    locations = [decode(location) for location in locations]
    return [UserLocation(**location) for location in locations]


async def save_for(redis_cli: Redis, user_id: str, location: Location):
    await redis_cli.geoadd(
        KEY, latitude=str(location.latitude), longitude=str(location.longitude), member=str(user_id)
    )
    await redis_cli.hmset_dict(
        f"user:{user_id}:location",
        user_id=user_id,
        latitude=str(location.latitude),
        longitude=str(location.longitude),
        course=str(location.course),
        ts=str(time.time()),
    )
