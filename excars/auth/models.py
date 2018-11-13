import peewee

from excars.db import database


class User(peewee.Model):
    username = peewee.CharField(unique=True)
    email = peewee.CharField(index=True)

    class Meta:
        database = database
        table_name = 'users'
