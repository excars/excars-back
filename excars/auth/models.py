import peewee

from excars.app import db


class User(peewee.Model):
    username = peewee.CharField(unique=True)
    email = peewee.CharField(index=True)

    class Meta:
        database = db
        table_name = 'users'
