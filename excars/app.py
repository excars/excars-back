import sanic
import sanic_cors

from excars import auth, db, redis, settings, ws

app = sanic.Sanic()
app.config.from_object(settings)


@app.middleware('request')
async def user(request):
    request['user'] = ''


sanic_cors.CORS(app, automatic_options=True)

app.register_listener(db.init, 'before_server_start')
app.register_listener(auth.init, 'before_server_start')
app.register_listener(redis.setup_redis, 'before_server_start')
app.register_listener(redis.stop_redis, 'before_server_stop')


app.blueprint(ws.bp)
