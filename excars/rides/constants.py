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
    RIDE_ACCEPTED = 'RIDE_ACCEPTED'
    RIDE_DECLINED = 'RIDE_DECLINED'
    RIDE_CANCELLED = 'RIDE_CANCELLED'

    SOCKET_CLOSE = '_WEBSOCKET_CLOSE'
    SOCKET_OPEN = '_WEBSOCKET_OPEN'


class RideRequestStatus:
    REQUESTED = 'requested'
    ACCEPTED = 'accepted'
    DECLINED = 'declined'
