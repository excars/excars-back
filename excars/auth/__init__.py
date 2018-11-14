from sanic_jwt import Initialize

from . import views

__all__ = ['init']


def init(app, loop):
    del loop
    Initialize(
        app,
        authenticate=views.authenticate,
        retrieve_user=views.retrieve_user
    )
