def create_tables(db):
    from excars.auth import models as auth_models
    from social_flask_peewee import models as social_models

    with db:
        db.create_tables([
            auth_models.User,

            social_models.FlaskStorage.user,
            social_models.FlaskStorage.nonce,
            social_models.FlaskStorage.association,
            social_models.FlaskStorage.code,
            social_models.FlaskStorage.partial,
        ], safe=True)
