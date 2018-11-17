import sanic
import sanic_cors

from excars import auth, db, redis, settings, ws


def create_app():
    app = sanic.Sanic()
    app.config.from_object(settings)

    sanic_cors.CORS(app, automatic_options=True)

    app.blueprint(ws.bp)
    setup_middlewares(app)

    auth.init(app)

    return app


def setup_listeners(app):
    app.register_listener(db.init, 'before_server_start')
    app.register_listener(redis.setup_redis, 'before_server_start')
    app.register_listener(redis.stop_redis, 'before_server_stop')


def setup_middlewares(app):
    async def user(request):
        request['user'] = ''
    app.register_middleware(user, 'request')


application = create_app()
setup_listeners(application)
