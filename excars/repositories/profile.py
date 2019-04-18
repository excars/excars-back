from aioredis import Redis

from excars.models.rides import Profile


def _get_key(user_id: str):
    return f"user:{user_id}"


async def save(redis_cli: Redis, profile: Profile):
    await redis_cli.set(_get_key(profile.user_id), profile.to_string())
