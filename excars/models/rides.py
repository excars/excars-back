from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from excars.models.profiles import Profile, Role


class RideRequestStatus(str, Enum):
    requested = "requested"
    accepted = "accepted"
    declined = "declined"


class RideRequest(BaseModel):
    sender: Profile
    receiver: Profile
    status: RideRequestStatus

    @property
    def ride_uid(self) -> int:
        return self.driver.user_id

    @property
    def driver(self) -> Profile:
        return self._get_profile_by_role(Role.driver)

    @property
    def passenger(self) -> Profile:
        return self._get_profile_by_role(Role.hitchhiker)

    def _get_profile_by_role(self, role: Role) -> Profile:
        if self.sender.role == role:
            return self.sender
        if self.receiver.role == role:
            return self.receiver
        raise Exception()


class RideRequestCreate(BaseModel):
    receiver: int


class RideRequestUpdate(BaseModel):
    status: RideRequestStatus
    passenger_id: Optional[int]


class Passenger(BaseModel):
    profile: Profile
    status: RideRequestStatus


class Ride(BaseModel):
    ride_id: int
    driver: Profile
    passengers: List[Passenger]
