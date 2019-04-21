import asyncio
from typing import List

from aioredis import Redis

from excars.models.locations import UserLocation

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
