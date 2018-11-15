import concurrent.futures

import requests.exceptions
import sanic_jwt.exceptions
import social_core.exceptions

from . import models, strategies


async def authenticate(request, *args, **kwargs):
    del args, kwargs
    request['auth_data'] = request.json
    strategy = strategies.load_strategy(request)

    backend = strategies.load_backend(strategy)
    backend.REDIRECT_STATE = False
    backend.STATE_PARAMETER = False
    backend.redirect_uri = request.json.get('redirect_uri')

    app = request.app
    with concurrent.futures.ThreadPoolExecutor() as pool:
        try:
            user = await app.loop.run_in_executor(pool, backend.complete)
        except (social_core.exceptions.AuthCanceled, requests.exceptions.HTTPError):
            raise sanic_jwt.exceptions.AuthenticationFailed()

    email_domain = user.email.partition('@')[2]
    if email_domain not in app.config.SOCIAL_AUTH_ALLOWED_EMAIL_DOMAINS:
        raise sanic_jwt.exceptions.AuthenticationFailed()

    return {
        'user_id': user.id
    }


async def retrieve_user(request, payload, *args, **kwargs):
    del request, args, kwargs
    if payload:
        user_id = payload.get('user_id', None)
        try:
            user = models.User.get_by_id(user_id)
        except models.User.DoesNotExist:
            return None

        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }

    return None
