import asyncio
import time
from typing import List

from aioredis import Redis

from excars.models.locations import Location, UserLocation

KEY = "user:locations"


async def list_for(redis_cli: Redis, user_id: int) -> List[UserLocation]:
    if await redis_cli.zrank(KEY, user_id) is None:
        return []

    geomembers = await redis_cli.georadiusbymember(KEY, member=user_id, radius=50, unit="km")

    locations = await asyncio.gather(
        *[redis_cli.hgetall(f"user:{geomember.decode()}:location") for geomember in geomembers]
    )
    # locations = [redis_utils.decode(location) for location in locations]

    return [UserLocation(**location) for location in locations]


async def save_for(redis_cli: Redis, user_id: int, location: Location):
    await redis_cli.geoadd(KEY, latitude=location.latitude, longitude=location.longitude, member=str(user_id))
    await redis_cli.hmset_dict(
        f"user:{user_id}:location",
        user_id=user_id,
        latitude=location.latitude,
        longitude=location.longitude,
        course=location.course,
        ts=time.time(),
    )
