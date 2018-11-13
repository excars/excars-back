import aioredis
import sanic
from playhouse.db_url import connect

from excars import settings
from excars.db import create_tables
from excars.ws import location

app = sanic.Sanic()
app.config.from_object(settings)


@app.middleware('request')
async def user(request):
    import random, string
    request['user'] = "".join([random.SystemRandom().choice(string.digits + string.ascii_letters) for _ in range(10)])


@app.listener('before_server_start')
async def setup_redis(app, loop):
    app.redis = await aioredis.create_redis_pool(
        app.config.REDIS_HOST,
        db=app.config.REDIS_DB,
        minsize=app.config.REDIS_POOL_MIN,
        maxsize=app.config.REDIS_POOL_MAX,
    )


@app.listener('before_server_stop')
async def stop_redis(app, loop):
    app.redis.close()


app.blueprint(location.bp)
db = connect(app.config.DB_URL)
# create_tables(db)
