import sanic.exceptions
import sanic.response
import sanic_jwt

from excars.auth import utils as auth_utils

from . import factories, repositories, schemas

bp = sanic.Blueprint('rides')


@bp.route('/api/rides/join', methods=['POST'])
@sanic_jwt.inject_user()
@sanic_jwt.protected()
async def join(request, user, *args, **kwargs):
    del args, kwargs

    payload = request.json

    data, errors = schemas.JoinPayload().load(payload)
    if errors:
        return sanic.response.json(
            errors,
            status=400,
        )

    profile = factories.make_profile(user, data['role'], data['destination'])

    redis_cli = request.app.redis
    await repositories.ProfileRepository(redis_cli).save(profile)

    return sanic.response.json(
        schemas.ProfileSchema().dump(profile).data
    )


@bp.route('/api/profiles/<uid:uuid>')
@sanic_jwt.protected()
async def retrieve_profile(request, uid):
    return await _retrieve_profile(uid, request.app.redis)


@bp.route('/api/profiles/me')
@sanic_jwt.protected()
async def retrieve_me(request):
    user_uid = auth_utils.extract_user_uid(request)
    return await _retrieve_profile(user_uid, request.app.redis)


async def _retrieve_profile(uid, redis_cli):
    profile = await repositories.ProfileRepository(redis_cli).get(uid)

    if not profile:
        raise sanic.exceptions.NotFound('Not Found')

    data = schemas.ProfileSchema().dump(profile).data

    return sanic.response.json(data)
