from fastapi import FastAPI

from excars import api, oauth2_redirect, redis

app = FastAPI(debug=True)
app.include_router(api.v1.router, prefix="/api/v1")
app.include_router(oauth2_redirect.router)


@app.on_event("startup")
async def startup():
    app.redis_cli = await redis.setup()


@app.on_event("shutdown")
async def shutdown():
    await redis.stop(app.redis_cli)
