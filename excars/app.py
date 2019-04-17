import sanic
import sanic_cors

from excars import auth, db, logging, redis, rides, settings, ws


def create_app():
    app = sanic.Sanic()
    app.config.from_object(settings)

    sanic_cors.CORS(app, automatic_options=True)

    auth.init(app)
    rides.init(app)
    ws.init(app)

    return app


def setup_listeners(app):
    app.register_listener(db.setup, "before_server_start")
    app.register_listener(redis.setup, "before_server_start")
    app.register_listener(logging.setup, "before_server_start")
    app.register_listener(redis.stop, "before_server_stop")


application = create_app()
setup_listeners(application)
