import typing

import marshmallow
from marshmallow import fields, validate

from . import constants, entities


class DestinationSchema(marshmallow.Schema):
    name = fields.Str(required=True)
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)

    @marshmallow.post_load
    def make_destination(self, data):  # pylint: disable=no-self-use
        return entities.Destination(**data)


class ProfileSchema(marshmallow.Schema):
    uid = fields.Str(required=True)
    name = fields.Str(required=True)
    avatar = fields.Str(required=True)
    plate = fields.Str(required=True)
    role = fields.Str(required=True)
    destination = fields.Nested(DestinationSchema, required=True)

    @marshmallow.post_load
    def make_profile(self, data):  # pylint: disable=no-self-use
        return entities.Profile(**data)


class ProfileRedisSchema(marshmallow.Schema):
    uid = fields.Str(required=True)
    name = fields.Str(required=True)
    avatar = fields.Str(required=True)
    plate = fields.Str(required=True)
    role = fields.Str(required=True)
    dest_name = fields.Str(attribute='destination.name', required=True)
    dest_lat = fields.Float(attribute='destination.latitude', required=True)
    dest_lon = fields.Float(attribute='destination.longitude', required=True)

    @marshmallow.post_load
    def make_profile(self, data):  # pylint: disable=no-self-use
        return entities.Profile(**data)


class JoinPayload(marshmallow.Schema):
    role = fields.Str(
        validate=validate.OneOf(
            choices=[constants.Role.DRIVER, constants.Role.HITCHHIKER]
        ),
        required=True,
    )
    destination = fields.Nested(DestinationSchema, required=True)


class CreateRidePayload(marshmallow.Schema):
    receiver = fields.Str()


class UpdateRidePayload(marshmallow.Schema):
    status = fields.Str(
        validate=validate.OneOf(
            choices=[constants.RideRequestStatus.ACCEPTED, constants.RideRequestStatus.DECLINED]
        ),
        required=True,
    )

    def __init__(self, *args, role: typing.Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)
        if role == constants.Role.DRIVER:
            self.declared_fields['passenger_uid'] = fields.Str(required=True)
            self.fields['passenger_uid'] = fields.Str(required=True)


class WSLocationPayload(marshmallow.Schema):
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    course = fields.Float(required=True)


class RideRequestStreamSchema(marshmallow.Schema):
    type = fields.Str()
    ride_uid = fields.Str()
    sender_uid = fields.Str(attribute='sender.uid')
    receiver_uid = fields.Str(attribute='receiver.uid')


class PassengerSchema(marshmallow.Schema):
    profile = fields.Nested(ProfileSchema)
    status = fields.Str()


class RideSchema(marshmallow.Schema):
    uid = fields.Str()
    driver = fields.Nested(ProfileSchema)
    passengers = fields.Nested(PassengerSchema, many=True)


class UserLocationSchema(marshmallow.Schema):
    user_uid = fields.Str(required=True)
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    course = fields.Float(required=True)
    ts = fields.Float()

    @marshmallow.post_load
    def make_user_location(self, data):  # pylint: disable=no-self-use
        return entities.UserLocation(**data)


class MessageSchema(marshmallow.Schema):
    type = fields.Str(required=True)
    data = fields.Dict(required=True)


class UserLocationRedisSchema(marshmallow.Schema):
    user_uid = fields.Str(required=True)
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    course = fields.Float(required=True)
    ts = fields.Float(required=True)

    @marshmallow.post_load
    def make_user_location(self, data):  # pylint: disable=no-self-use
        return entities.UserLocation(**data)


class MapItemSchema(marshmallow.Schema):
    user_uid = fields.Str()
    role = fields.Str()
    location = fields.Nested(UserLocationSchema)
    has_same_ride = fields.Bool()
