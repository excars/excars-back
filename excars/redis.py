import uuid

import aioredis


async def setup(app, _):
    app.redis = await aioredis.create_redis_pool(
        app.config.REDIS_URL,
        db=app.config.REDIS_DB,
        minsize=app.config.REDIS_POOL_MIN,
        maxsize=app.config.REDIS_POOL_MAX,
    )


async def stop(app, _):
    app.redis.close()
    await app.redis.wait_closed()


def get_user_key(user_uid: uuid.uuid4) -> str:
    return f'user:{user_uid}'


def decode(data):
    return {k.decode(): v.decode() for k, v in data.items()}
