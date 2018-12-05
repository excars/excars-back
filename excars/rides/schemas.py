import marshmallow
from marshmallow import fields

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
    dest_name = fields.Str()
    dest_lat = fields.Float()
    dest_lon = fields.Float()

    @marshmallow.post_load
    def make_profile(self, data):  # pylint: disable=no-self-use
        return entities.Profile(
            uid=data['uid'],
            name=data['name'],
            avatar=data['avatar'],
            plate=data['plate'],
            role=data['role'],
            destination=entities.Destination(
                name=data['dest_name'],
                latitude=data['dest_lat'],
                longitude=data['dest_lon'],
            )
        )


class JoinPayload(marshmallow.Schema):
    role = fields.Str()
    destination = fields.Nested(DestinationSchema)
