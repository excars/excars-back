import aioredis
from aioredis import Redis

from excars import config


async def setup():
    return await aioredis.create_redis_pool(
        config.REDIS_HOST, db=config.REDIS_DB, minsize=config.REDIS_POOL_MIN, maxsize=config.REDIS_POOL_MAX
    )


async def stop(redis_cli: Redis):
    redis_cli.close()
    await redis_cli.wait_closed()
