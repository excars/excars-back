from excars.ws import event

from . import constants, factories, repositories, schemas


@event.consume(constants.MessageType.RIDE_REQUESTED)
async def request_ride(request, ws, message, user):
    return await _send_event(constants.MessageType.RIDE_REQUESTED, request, ws, message, user)


@event.consume(constants.MessageType.RIDE_ACCEPTED)
async def ride_accepted(request, ws, message, user):
    return await _send_event(constants.MessageType.RIDE_ACCEPTED, request, ws, message, user)


@event.consume(constants.MessageType.RIDE_DECLINED)
async def ride_declined(request, ws, message, user):
    return await _send_event(constants.MessageType.RIDE_DECLINED, request, ws, message, user)


@event.consume(constants.MessageType.RIDE_CANCELLED)
async def ride_cancelled(request, ws, message, user):
    return await _send_event(constants.MessageType.RIDE_CANCELLED, request, ws, message, user)


async def _send_event(message_type, request, ws, message, user):
    del user

    data = schemas.RideStreamSchema().load(message).data

    redis_cli = request.app.redis
    ride = await repositories.RideRepository(redis_cli).get(data['uid'])

    sender = await repositories.ProfileRepository(redis_cli).get(ride.sender)
    receiver = await repositories.ProfileRepository(redis_cli).get(ride.receiver)

    message = factories.make_message(
        message_type,
        payload={
            'uid': ride.uid,
            'sender': schemas.ProfileSchema().dump(sender).data,
            'receiver': schemas.ProfileSchema().dump(receiver).data,
        }
    )

    await ws.send(schemas.MessageSchema().dumps(message).data)
