from unittest import mock

from excars.auth import init, views


def test_init():
    app = mock.MagicMock()

    with mock.patch('excars.auth.Initialize') as jwt_init:
        init(app, mock.MagicMock())

    assert jwt_init.called
    assert jwt_init.call_args == mock.call(
        app,
        authenticate=views.authenticate,
        retrieve_user=views.retrieve_user
    )
