import pytest
from social_core.backends import google

from excars.auth import models, pipelines


@pytest.fixture
def google_oauth2_resp():
    return {
        'image': {
            'url': 'path/to/pic'
        }
    }


@pytest.fixture
def google_plus_resp():
    return {
        'picture': 'path/to/pic'
    }


@pytest.mark.parametrize(['backend', 'response', 'expected'], [
    (google.GoogleOAuth2, 'google_oauth2_resp', 'path/to/pic'),
    (google.GooglePlusAuth, 'google_plus_resp', 'path/to/pic'),
])
def test_save_avatar(request, mocker, backend, response, expected):
    user = models.User(username='user')
    user.save = mocker.MagicMock()
    strategy = mocker.MagicMock()
    response = request.getfixturevalue(response)

    pipelines.save_avatar(backend(strategy), user, response)

    assert user.avatar == expected
    assert user.save.called


@pytest.mark.parametrize('backend', [
    google.GoogleOAuth2,
    google.GooglePlusAuth,
])
def test_save_avatar_no_avatar(mocker, backend):
    user = models.User(username='user')
    user.save = mocker.MagicMock()
    strategy = mocker.MagicMock()

    pipelines.save_avatar(backend(strategy), user, {})

    assert user.avatar == ''
    assert user.save.called is False
