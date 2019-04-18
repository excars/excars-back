import aioredis
from fastapi import FastAPI

from excars import api, config, oauth2_redirect

app = FastAPI(debug=True)
app.include_router(api.v1.router, prefix="/api/v1")
app.include_router(oauth2_redirect.router)


@app.on_event("startup")
async def startup():
    app.redis_cli = await aioredis.create_redis_pool(
        config.REDIS_HOST, db=config.REDIS_DB, minsize=config.REDIS_POOL_MIN, maxsize=config.REDIS_POOL_MAX
    )


@app.on_event("shutdown")
async def shutdown():
    redis_cli = app.redis_cli
    redis_cli.close()
    await redis_cli.wait_closed()
