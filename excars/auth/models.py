import peewee

from excars.db import database


class User(peewee.Model):
    username = peewee.CharField(unique=True)
    email = peewee.CharField(index=True)
    first_name = peewee.CharField(default='')
    last_name = peewee.CharField(default='')
    full_name = peewee.CharField(default='')

    class Meta:
        database = database
        table_name = 'users'
