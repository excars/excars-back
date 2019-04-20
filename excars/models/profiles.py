from decimal import Decimal
from enum import Enum

from pydantic import BaseModel

from excars.models.user import User


class Role(str, Enum):
    driver = "driver"
    hitchhiker = "hitchhiker"

    @classmethod
    def opposite(cls, role: "Role") -> "Role":
        role_map = {cls.driver: cls.hitchhiker, cls.hitchhiker: cls.driver}
        return role_map[role]


class Destination(BaseModel):
    name: str
    latitude: Decimal
    longitude: Decimal


class JoinRequest(BaseModel):
    role: Role
    destination: Destination


class Profile(BaseModel):
    user_id: str
    name: str
    avatar: str
    role: Role
    destination: Destination

    @classmethod
    def from_user(cls, user: User, role: Role, destination: Destination):
        return cls(user_id=user.user_id, name=user.name, avatar=user.avatar, role=role, destination=destination)
