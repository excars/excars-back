from unittest import mock

import pytest

from excars.settings._env import get_bool, get_list


@pytest.mark.parametrize(['given', 'expected'], [
    ('True', True),
    ('true', True),
    ('1', True),
    ('0', False),
    ('False', False),
    (None, False),
])
def test_get_bool(given, expected):
    with mock.patch('os.getenv', return_value=given):
        value = get_bool('DEBUG')
    assert value == expected


@pytest.mark.parametrize(['given', 'expected'], [
    (None, []),
    ('excars.com', ['excars.com']),
    ('excars.com, google.com', ['excars.com', 'google.com'])
])
def test_get_list(given, expected):
    with mock.patch('os.getenv', return_value=given):
        value = get_list('LIST')
    assert value == expected


def test_get_list_returns_default():
    with mock.patch('os.getenv', return_value=None):
        value = get_list('LIST', default=['excars.com'])
    assert value == ['excars.com']
