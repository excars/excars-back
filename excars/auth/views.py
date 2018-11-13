import concurrent.futures

from social_core.backends.google import GoogleOAuth2
from social_flask_peewee.models import FlaskStorage

from . import models
from .strategy import SanicStrategy


def load_strategy(request=None):
    return SanicStrategy(FlaskStorage, request=request)


def load_backend(strategy, redirect_uri=''):
    return GoogleOAuth2(strategy, redirect_uri)


async def authenticate(request, *args, **kwargs):
    del args, kwargs
    request['auth_data'] = request.json
    strategy = load_strategy(request)

    backend = load_backend(strategy)
    backend.REDIRECT_STATE = False
    backend.STATE_PARAMETER = False

    with concurrent.futures.ThreadPoolExecutor() as pool:
        user = await request.app.loop.run_in_executor(pool, backend.complete)

    return {
        'user_id': user.id
    }


async def retrieve_user(request, payload, *args, **kwargs):
    del request, args, kwargs
    if payload:
        user_id = payload.get('user_id', None)
        user = models.User.get_by_id(user_id)

        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }

    return None
