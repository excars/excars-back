from playhouse import db_url
from social_core.utils import module_member
from social_flask_peewee import models as social_models

from .settings import db as db_settings

database = db_url.connect(db_settings.DATABASE_URL, database=None)


async def setup(app, _):
    _init_db(app, database)
    social_models.init_social(app, database)
    create_tables(app, database)


def _init_db(app, db):
    connection_params = db_url.parse(app.config.DATABASE_URL)
    return db.init(connection_params['database'])


def create_tables(app, db):
    models = get_models(app)

    with db:
        db.create_tables(models, safe=True)


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
