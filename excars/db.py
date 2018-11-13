from playhouse import db_url
from social_core.utils import module_member
from social_flask_peewee import models as social_models
from social_flask_peewee.models import init_social


def get_models(app):
    models = [
        social_models.FlaskStorage.user,
        social_models.FlaskStorage.nonce,
        social_models.FlaskStorage.association,
        social_models.FlaskStorage.code,
        social_models.FlaskStorage.partial,
    ]

    models += list(map(module_member, app.config.APP_MODELS))

    return models


def create_tables(app, db):
    models = get_models(app)

    with app.db:
        db.create_tables(models, safe=True)


def init_db(app, db):
    connection_params = db_url.parse(app.config.DB_DSN)
    return db.init(connection_params['database'])


async def setup_db(app, loop):
    del loop
    init_db(app, app.db)
    init_social(app, app.db)
    create_tables(app, app.db)
