import typing
from dataclasses import dataclass

from . import constants


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
class RideRequest:
    sender: Profile
    receiver: Profile
    status: str

    @property
    def ride_uid(self) -> str:
        return self.driver.uid

    @property
    def driver(self) -> Profile:
        return self._get_profile_by_role(constants.Role.DRIVER)

    @property
    def passenger(self) -> Profile:
        return self._get_profile_by_role(constants.Role.HITCHHIKER)

    def _get_profile_by_role(self, role) -> Profile:
        if self.sender.role == role:
            return self.sender
        if self.receiver.role == role:
            return self.receiver
        raise Exception()


@dataclass
class Passenger:
    profile: Profile
    status: str


@dataclass
class Ride:
    uid: str
    driver: Profile
    passengers: typing.List[Passenger]


@dataclass
class UserLocation:
    user_uid: str
    latitude: float
    longitude: float
    course: float


@dataclass
class Message:
    type: str
    data: typing.Dict[str, typing.Any]


@dataclass
class MapItem:
    user_uid: str
    role: typing.Optional[str]
    location: UserLocation
    has_same_ride: bool
