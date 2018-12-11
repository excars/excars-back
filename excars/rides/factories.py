import typing

from excars.auth import models as auth_models

from . import constants, entities


def make_profile(
        user: auth_models.User,
        role: typing.Optional[str] = None,
        destination: typing.Optional[entities.Destination] = None
) -> entities.Profile:
    return entities.Profile(
        uid=str(user.uid),
        name=user.get_name(),
        avatar=user.avatar,
        plate=user.plate,
        role=role,
        destination=destination,
    )


def make_ride_request(
        sender: entities.Profile,
        receiver: entities.Profile,
        status: typing.Optional[str] = None
) -> entities.RideRequest:
    assert sender.role != receiver.role, 'Roles must be different'

    if not status:
        if sender.role == constants.Role.DRIVER:
            status = constants.RideRequestStatus.OFFERED
        elif sender.role == constants.Role.HITCHHIKER:
            status = constants.RideRequestStatus.REQUESTED
        else:
            raise Exception(f'Unknown role for profile: {sender.uid}')

    return entities.RideRequest(sender=sender, receiver=receiver, status=status)


def make_user_location(
        user: auth_models.User,
        latitude: float,
        longitude: float,
        course: float
) -> entities.UserLocation:
    return entities.UserLocation(
        user_uid=str(user.uid),
        latitude=latitude,
        longitude=longitude,
        course=course,
    )


def make_message(
        message_type: str,
        payload: typing.Dict[str, typing.Any]
) -> entities.Message:
    return entities.Message(
        type=message_type,
        data=payload
    )
