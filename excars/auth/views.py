import concurrent.futures

from social_core.backends.google import GoogleOAuth2
from social_flask_peewee.models import FlaskStorage

from .strategy import SanicStrategy


def load_strategy(request=None):
    return SanicStrategy(request=request, storage=FlaskStorage)


def load_backend(strategy, redirect_uri=''):
    return GoogleOAuth2(strategy, redirect_uri)


async def authenticate(request, *args, **kwargs):
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
