import sanic.exceptions
import sanic.response
import sanic_jwt

from . import factories, repositories, schemas

bp = sanic.Blueprint('rides')


@bp.route('/api/rides/join', methods=['POST'])
@sanic_jwt.inject_user()
@sanic_jwt.protected()
async def join(request, user, *args, **kwargs):
    del args, kwargs

    payload = request.json
    data = schemas.JoinPayload().load(payload).data

    profile = factories.make_profile(user, data['role'], data['destination'])

    redis_cli = request.app.redis
    await repositories.ProfileRepository(redis_cli).save(profile)

    return sanic.response.json({
        'status': 'OK'
    })


@bp.route('/api/profiles/<uid:uuid>')
@sanic_jwt.protected()
async def retrieve_profile(request, uid):
    redis_cli = request.app.redis
    profile = await repositories.ProfileRepository(redis_cli).get(uid)
    data = schemas.ProfileSchema().dump(profile).data

    return sanic.response.json(data)
