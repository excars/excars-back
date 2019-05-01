import sentry_sdk
from fastapi import FastAPI
from sentry_asgi import SentryMiddleware

from excars import api, config, oauth2_redirect, redis

app = FastAPI(title="ExCars", debug=config.DEBUG)
app.include_router(api.v1.router, prefix="/api/v1")
app.include_router(oauth2_redirect.router)

if config.SENTRY_DSN:  # pragma: no cover
    sentry_sdk.init(dsn=config.SENTRY_DSN)
    app.add_middleware(SentryMiddleware)


@app.on_event("startup")
async def startup():
    app.redis_cli = await redis.setup()


@app.on_event("shutdown")
async def shutdown():
    await redis.stop(app.redis_cli)
