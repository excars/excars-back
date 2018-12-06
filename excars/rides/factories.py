import typing

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
