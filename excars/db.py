from social_core.utils import module_member
from social_flask_peewee import models as social_models


def create_tables(app, db):
    tables = [
        social_models.FlaskStorage.user,
        social_models.FlaskStorage.nonce,
        social_models.FlaskStorage.association,
        social_models.FlaskStorage.code,
        social_models.FlaskStorage.partial,
    ]

    tables.extend(list(map(module_member, app.config.APP_MODELS)))

    with db:
        db.create_tables(tables, safe=True)
