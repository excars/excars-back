import aioredis


async def setup_redis(app, _):
    app.redis = await aioredis.create_redis_pool(
        app.config.REDIS_HOST,
        db=app.config.REDIS_DB,
        minsize=app.config.REDIS_POOL_MIN,
        maxsize=app.config.REDIS_POOL_MAX,
    )


async def stop_redis(app, _):
    app.redis.close()
