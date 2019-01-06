import time
import typing

from excars.auth import models as auth_models

from . import entities


def make_profile(
        user: auth_models.User,
        role: typing.Optional[str] = None,
        destination: typing.Optional[entities.Destination] = None,
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
        status: str
) -> entities.RideRequest:
    assert sender.role != receiver.role, 'Roles must be different'
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
        ts=time.time(),
    )


def make_message(
        message_type: str,
        payload: typing.Dict[str, typing.Any]
) -> entities.Message:
    return entities.Message(
        type=message_type,
        data=payload
    )


def make_map_item(
        profile: entities.Profile,
        location: entities.UserLocation,
        has_same_ride: bool,
) -> entities.MapItem:
    return entities.MapItem(
        user_uid=profile.uid,
        role=profile.role,
        location=location,
        has_same_ride=has_same_ride,
    )
