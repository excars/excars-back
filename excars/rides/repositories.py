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

    async def get(self, user_uid: str) -> typing.Optional[entities.Profile]:
        payload = redis_utils.decode(await self.redis_cli.hgetall(f'user:{user_uid}'))

        data, errors = schemas.ProfileRedisSchema().load(payload)
        if errors:
            return None

        return data
