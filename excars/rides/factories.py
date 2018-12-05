from . import entities


def make_profile(user, role, destination) -> entities.Profile:
    return entities.Profile(
        uid=str(user.uid),
        name=user.get_name(),
        avatar=user.avatar,
        plate=user.plate,
        role=role,
        destination=destination,
    )
