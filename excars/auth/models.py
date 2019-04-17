import uuid

import peewee

from excars.db import database


class User(peewee.Model):
    uid = peewee.UUIDField(unique=True, default=uuid.uuid4)
    username = peewee.CharField(unique=True)
    email = peewee.CharField(index=True)
    first_name = peewee.CharField(default="")
    last_name = peewee.CharField(default="")
    avatar = peewee.CharField(max_length=1024, default="")
    plate = peewee.CharField(max_length=10, default="")

    class Meta:
        database = database
        table_name = "users"

    def get_name(self):
        if self.first_name or self.last_name:
            return " ".join([self.first_name, self.last_name]).strip()

        return self.username

    def to_dict(self):
        return {
            "user_id": str(self.uid),
            "uid": str(self.uid),
            "username": self.username,
            "first_name": self.first_name,
            "name": self.get_name(),
            "email": self.email,
            "avatar": self.avatar,
        }
