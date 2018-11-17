import uuid

import peewee

from excars.db import database


class User(peewee.Model):
    uid = peewee.UUIDField(unique=True, default=uuid.uuid4)
    username = peewee.CharField(unique=True)
    email = peewee.CharField(index=True)
    first_name = peewee.CharField(default='')
    last_name = peewee.CharField(default='')
    full_name = peewee.CharField(default='')

    class Meta:
        database = database
        table_name = 'users'

    def to_dict(self):
        return {
            'user_id': self.id,
            'uid': str(self.uid),
            'username': self.username,
            'email': self.email,
        }
