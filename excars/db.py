from social_core.utils import module_member
from social_flask_peewee import models as social_models


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

    with db:
        db.create_tables(models, safe=True)
