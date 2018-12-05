import marshmallow
from marshmallow import fields, validate

from . import constants as const
from . import entities


class DestinationSchema(marshmallow.Schema):
    name = fields.Str()
    latitude = fields.Float()
    longitude = fields.Float()

    @marshmallow.post_load
    def make_destination(self, data):  # pylint: disable=no-self-use
        return entities.Destination(**data)


class ProfileSchema(marshmallow.Schema):
    uid = fields.Str()
    name = fields.Str()
    avatar = fields.Str()
    plate = fields.Str()
    role = fields.Str()
    destination = fields.Nested(DestinationSchema)

    @marshmallow.post_load
    def make_profile(self, data):  # pylint: disable=no-self-use
        return entities.Profile(**data)


class ProfileRedisSchema(marshmallow.Schema):
    uid = fields.Str()
    name = fields.Str()
    avatar = fields.Str()
    plate = fields.Str()
    role = fields.Str()
    dest_name = fields.Str(attribute='destination.name')
    dest_lat = fields.Float(attribute='destination.latitude')
    dest_lon = fields.Float(attribute='destination.longitude')

    @marshmallow.post_load
    def make_profile(self, data):  # pylint: disable=no-self-use
        return entities.Profile(**data)


class JoinPayload(marshmallow.Schema):
    role = fields.Str(validate=validate.OneOf(choices=[const.Role.DRIVER, const.Role.HITCHHIKER]))
    destination = fields.Nested(DestinationSchema)
