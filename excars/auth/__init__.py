from sanic_jwt import Initialize

from . import views

__all__ = ["init"]


def init(app):
    Initialize(
        app,
        authenticate=views.authenticate,
        retrieve_user=views.retrieve_user,
        query_string_set=True,
        query_string_strict=False,
        expiration_delta=app.config.JWT_EXPIRATION_DELTA,
    )
