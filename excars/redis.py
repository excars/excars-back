import aioredis


async def setup(app, _):
    app.redis = await aioredis.create_redis_pool(
        app.config.REDIS_HOST,
        db=app.config.REDIS_DB,
        minsize=app.config.REDIS_POOL_MIN,
        maxsize=app.config.REDIS_POOL_MAX,
    )


async def stop(app, _):
    app.redis.close()
    await app.redis.wait_closed()


def decode(data):
    return {k.decode(): v.decode() for k, v in data.items()}
