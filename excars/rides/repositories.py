import typing

from excars import redis as redis_utils

from . import entities, schemas


class ProfileRepository:

    def __init__(self, redis_cli):
        self.redis_cli = redis_cli

    async def save(self, profile: entities.Profile):
        await self.redis_cli.hmset_dict(
            f'user:{profile.uid}',
            **schemas.ProfileRedisSchema().dump(profile).data
        )

    async def get(self, user_uid) -> typing.Optional[entities.Profile]:
        data = redis_utils.decode(await self.redis_cli.hgetall(f'user:{user_uid}'))
        if not data:
            return None
        return schemas.ProfileRedisSchema().load(data).data
