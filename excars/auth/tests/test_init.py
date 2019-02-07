from unittest import mock

from excars.auth import init, views


def test_init():
    app = mock.MagicMock()

    with mock.patch('excars.auth.Initialize') as jwt_init:
        init(app)

    assert jwt_init.called
    assert jwt_init.call_args == mock.call(
        app,
        authenticate=views.authenticate,
        retrieve_user=views.retrieve_user,
        query_string_set=True,
        query_string_strict=False,
        expiration_delta=app.config.JWT_EXPIRATION_DELTA,
    )
