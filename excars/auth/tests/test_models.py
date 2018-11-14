import pytest

from excars.auth import models


@pytest.mark.require_db
def test_create_model():
    user = models.User.create(
        username='user',
        email='user@excars.com',
    )

    assert user.first_name == ''
    assert user.last_name == ''
    assert user.full_name == ''
