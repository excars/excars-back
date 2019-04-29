from typing import Optional

from aioredis import Redis

from excars.models.user import User


def _get_key(user_id: int) -> str:
    return f"users:{user_id}"


async def get(redis_cli: Redis, user_id: int) -> Optional[User]:
    data = await redis_cli.get(_get_key(user_id))
    if not data:
        return None
    return User.parse_raw(data)


async def save(redis_cli: Redis, user: User) -> None:
    await redis_cli.set(_get_key(user.user_id), user.json())
