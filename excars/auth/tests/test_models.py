import uuid

import pytest

from excars.auth import models


@pytest.mark.require_db
def test_create_model():
    user = models.User.create(
        username='user',
        email='user@excars.com',
    )

    assert user.uid

    assert user.first_name == ''
    assert user.last_name == ''
    assert user.avatar == ''


def test_user_to_dict():
    user = models.User(
        username='user',
        email='user@excars.com',
        uid=uuid.uuid4(),
    )

    assert user.to_dict() == {
        'user_id': str(user.uid),
        'uid': str(user.uid),
        'username': user.username,
        'first_name': user.first_name,
        'name': user.get_name(),
        'email': user.email,
        'avatar': '',
    }


@pytest.mark.parametrize(['username', 'first_name', 'last_name', 'expected'], [
    ('user', '', '', 'user'),
    ('user', 'Al', '', 'Al'),
    ('user', 'Al', 'Green', 'Al Green'),
    ('user', '', 'Green', 'Green')
])
def test_get_name(username, first_name, last_name, expected):
    user = models.User(
        username=username,
        first_name=first_name,
        last_name=last_name,
    )

    assert user.get_name() == expected
