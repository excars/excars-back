from decimal import Decimal
from enum import Enum

from pydantic import BaseModel


class Role(str, Enum):
    driver = "driver"
    hitchhiker = "hitchhiker"

    @classmethod
    def opposite(cls, role: "Role") -> str:
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
