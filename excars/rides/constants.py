class Role:
    DRIVER = 'driver'
    HITCHHIKER = 'hitchhiker'

    @classmethod
    def opposite(cls, role: str) -> str:
        role_map = {
            cls.HITCHHIKER: cls.DRIVER,
            cls.DRIVER: cls.HITCHHIKER
        }
        return role_map[role]


class MessageType:
    LOCATION = 'LOCATION'
    MAP = 'MAP'
    RIDE_REQUESTED = 'RIDE_REQUESTED'
    RIDE_REQUEST_ACCEPTED = 'RIDE_REQUEST_ACCEPTED'
    RIDE_REQUEST_DECLINED = 'RIDE_REQUEST_DECLINED'
    RIDE_UPDATED = 'RIDE_UPDATED'
    RIDE_CANCELLED = 'RIDE_CANCELLED'


class RideRequestStatus:
    REQUESTED = 'requested'
    ACCEPTED = 'accepted'
    DECLINED = 'declined'
