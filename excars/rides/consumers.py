from excars.ws import event

from . import constants, factories, repositories, schemas


@event.consume(constants.MessageType.RIDE_REQUESTED)
async def ride_requested(request, ws, message, user):
    return await _send_ride_request_event(constants.MessageType.RIDE_REQUESTED, request, ws, message, user)


@event.consume(constants.MessageType.RIDE_REQUEST_ACCEPTED)
async def ride_request_accepted(request, ws, message, user):
    return await _send_ride_request_event(constants.MessageType.RIDE_REQUEST_ACCEPTED, request, ws, message, user)


@event.consume(constants.MessageType.RIDE_REQUEST_DECLINED)
async def ride_request_declined(request, ws, message, user):
    return await _send_ride_request_event(constants.MessageType.RIDE_REQUEST_DECLINED, request, ws, message, user)


async def _send_ride_request_event(message_type, request, ws, message, user):
    del user

    data = schemas.RideRequestStreamSchema().load(message).data
    redis_cli = request.app.redis

    sender = await repositories.ProfileRepository(redis_cli).get(data['sender']['uid'])
    receiver = await repositories.ProfileRepository(redis_cli).get(data['receiver']['uid'])

    message = factories.make_message(
        message_type,
        payload={
            'ride_uid': data['ride_uid'],
            'sender': schemas.ProfileSchema().dump(sender).data,
            'receiver': schemas.ProfileSchema().dump(receiver).data,
        }
    )

    await ws.send(schemas.MessageSchema().dumps(message).data)


@event.consume(constants.MessageType.RIDE_UPDATED)
async def ride_updated(request, ws, message, user):
    return await _send_ride_event(constants.MessageType.RIDE_UPDATED, request, ws, message, user)


@event.consume(constants.MessageType.RIDE_CANCELLED)
async def ride_cancelled(request, ws, message, user):
    return await _send_ride_event(constants.MessageType.RIDE_CANCELLED, request, ws, message, user)


async def _send_ride_event(message_type, request, ws, message, user):
    del request, user

    message = factories.make_message(
        message_type,
        payload={
            'ride_uid': message['ride_uid'],
        }
    )

    await ws.send(schemas.MessageSchema().dumps(message).data)
