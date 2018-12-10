import typing
import uuid

from excars.auth import models as auth_models

from . import entities


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


def make_ride(sender_uid: str, receiver_uid: str) -> entities.Ride:
    return entities.Ride(
        uid=str(uuid.uuid4()),
        sender=str(sender_uid),
        receiver=str(receiver_uid),
    )


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
