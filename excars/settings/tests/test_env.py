from unittest import mock

import pytest

from excars.settings._env import get_bool


@pytest.mark.parametrize(['given', 'expected'], [
    ('True', True),
    ('true', True),
    ('1', True),
    ('0', False),
    ('False', False),
])
def test_get_bool(given, expected):
    with mock.patch('os.getenv', return_value=given):
        value = get_bool('DEBUG')
    assert value == expected
