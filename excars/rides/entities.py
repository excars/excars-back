import typing
from dataclasses import dataclass


@dataclass
class Destination:
    name: str
    latitude: float
    longitude: float


@dataclass
class Profile:
    uid: str
    name: str
    avatar: str
    plate: str
    role: typing.Optional[str]
    destination: typing.Optional[Destination]


@dataclass
class Ride:
    uid: str
    sender: str
    receiver: str
