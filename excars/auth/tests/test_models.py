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
    assert user.full_name == ''


def test_user_to_dict():
    user = models.User(
        username='user',
        email='user@excars.com',
        uid=uuid.uuid4(),
    )

    assert user.to_dict() == {
        'user_id': user.id,
        'uid': str(user.uid),
        'username': user.username,
        'email': user.email,
    }
