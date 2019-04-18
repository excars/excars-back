from aioredis import Redis

from excars.models.rides import Profile


def _get_key(uid: str):
    return f"user:{uid}"


async def save(redis_cli: Redis, profile: Profile):
    await redis_cli.hmset_dict(
        key=_get_key(profile.user_id),
        uid=profile.user_id,
        name=profile.name,
        avatar=profile.avatar,
        role=profile.role,
        dest_name=profile.destination.name,
        dest_lat=str(profile.destination.latitude),
        dest_lon=str(profile.destination.longitude),
    )
