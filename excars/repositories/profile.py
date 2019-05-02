from typing import Optional

from aioredis import Redis

from excars import config
from excars.models.profiles import Profile


def _get_key_for(user_id: str) -> str:
    return f"users:{user_id}:profile"


async def save(redis_cli: Redis, profile: Profile):
    await redis_cli.set(_get_key_for(profile.user_id), profile.json())


async def get(redis_cli: Redis, user_id: str) -> Optional[Profile]:
    data = await redis_cli.get(_get_key_for(user_id))
    if not data:
        return None
    return Profile.parse_raw(data)


async def delete(redis_cli: Redis, user_id: str) -> None:
    await redis_cli.delete(_get_key_for(user_id))


async def persist(redis_cli: Redis, user_id: str) -> None:
    await redis_cli.persist(_get_key_for(user_id))


async def expire(redis_cli: Redis, user_id: str) -> None:
    await redis_cli.expire(_get_key_for(user_id), timeout=config.PROFILE_TTL)
