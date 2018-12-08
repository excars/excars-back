import sanic.exceptions
import sanic.response
import sanic_jwt

from . import factories, repositories, schemas

bp = sanic.Blueprint('rides')


@bp.route('/api/rides/join', methods=['POST'])
@sanic_jwt.inject_user()
@sanic_jwt.protected()
async def join(request, user):
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
    redis_cli = request.app.redis
    profile = await repositories.ProfileRepository(redis_cli).get(uid)

    if not profile:
        raise sanic.exceptions.NotFound('Not Found')

    data = schemas.ProfileSchema().dump(profile).data

    return sanic.response.json(data)


@bp.route('/api/profiles/me')
@sanic_jwt.inject_user()
@sanic_jwt.protected()
async def retrieve_me(request, user):
    redis_cli = request.app.redis
    profile = await repositories.ProfileRepository(redis_cli).get(user.uid)
    if not profile:
        profile = factories.make_profile(user)

    return sanic.response.json(
        schemas.ProfileSchema().dump(profile).data
    )


@bp.route('/api/rides', methods=['POST'])
@sanic_jwt.inject_user()
@sanic_jwt.protected()
async def create_ride(request, user):
    payload = request.json
    data, errors = schemas.CreateRidePayload().load(payload)
    if errors:
        return sanic.response.json(
            errors,
            status=400,
        )

    redis_cli = request.app.redis
    receiver = await repositories.ProfileRepository(redis_cli).get(data['receiver'])
    if not receiver:
        raise sanic.exceptions.NotFound('Not Found')

    ride = factories.make_ride(sender_uid=user.uid, receiver_uid=receiver.uid)
    await repositories.RideRepository(redis_cli).save(ride)
    await repositories.StreamRepository(redis_cli).request_ride(ride)

    return sanic.response.json(
        schemas.RideRedisSchema().dump(ride).data
    )


@bp.route('/api/rides/<uid:uuid>', methods=['PUT'])
@sanic_jwt.protected()
async def update_ride(request, uid, *args, **kwargs):
    del args, kwargs

    payload = request.json
    data, _ = schemas.UpdateRidePayload().load(payload)

    redis_cli = request.app.redis
    ride = await repositories.RideRepository(redis_cli).get(uid)

    await repositories.StreamRepository(redis_cli).update_ride(ride, data['status'])

    return sanic.response.json(
        schemas.RideRedisSchema().dump(ride).data
    )
