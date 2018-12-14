import sanic.exceptions
import sanic.response
import sanic_jwt

from . import constants, factories, repositories, schemas

bp = sanic.Blueprint('rides')


@bp.route('/api/rides/join', methods=['POST'])
@sanic_jwt.inject_user()
@sanic_jwt.protected()
async def join(request, user):
    data, errors = schemas.JoinPayload().load(request.json)
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
    data, errors = schemas.CreateRidePayload().load(request.json)
    if errors:
        return sanic.response.json(
            errors,
            status=400,
        )

    redis_cli = request.app.redis
    profile_repo = repositories.ProfileRepository(redis_cli)

    receiver = await profile_repo.get(data['receiver'])
    if not receiver:
        raise sanic.exceptions.NotFound('Not Found')

    sender = await profile_repo.get(user.uid)
    if not sender:
        role = constants.Role.opposite(receiver.role)
        sender = factories.make_profile(user, role, receiver.destination)
        await profile_repo.save(sender)

    ride_request = factories.make_ride_request(
        sender,
        receiver,
        status=constants.RideRequestStatus.REQUESTED,
    )
    await repositories.RideRepository(redis_cli).add(ride_request)
    await repositories.StreamRepository(redis_cli).ride_requested(ride_request)

    return sanic.response.json({
        'uid': ride_request.ride_uid
    })


@bp.route('/api/rides/<uid:uuid>', methods=['PUT'])
@sanic_jwt.inject_user()
@sanic_jwt.protected()
async def update_ride(request, uid, user):
    profile_repo = repositories.ProfileRepository(request.app.redis)
    ride_repo = repositories.RideRepository(request.app.redis)
    stream_repo = repositories.StreamRepository(request.app.redis)

    receiver = await profile_repo.get(user.uid)
    if not receiver:
        raise sanic.exceptions.NotFound('Not Found')

    schema = schemas.UpdateRidePayload(role=receiver.role).load(request.json)
    if schema.errors:
        return sanic.response.json(
            schema.errors,
            status=400,
        )

    sender = await profile_repo.get(schema.data.get('passenger_uid', uid))
    if not sender:
        raise sanic.exceptions.NotFound('Not Found')

    ride_request = factories.make_ride_request(sender, receiver, status=schema.data['status'])
    if not await ride_repo.exists(ride_request):
        raise sanic.exceptions.NotFound('Not Found')

    await ride_repo.add(ride_request)
    await stream_repo.ride_updated(ride_request)

    return sanic.response.json({
        'uid': ride_request.ride_uid
    })


@bp.route('/api/rides/<uid:uuid>', methods=['GET'])
@sanic_jwt.protected()
async def ride_details(request, uid):
    redis_cli = request.app.redis

    ride = await repositories.RideRepository(redis_cli).get(uid)
    if not ride:
        raise sanic.exceptions.NotFound('Not Found')

    return sanic.response.json(
        schemas.RideSchema().dump(ride).data
    )
