# pylint: disable=redefined-outer-name

import psycopg2
import psycopg2.extensions
import pytest
from playhouse import db_url
from social_flask_peewee.models import init_social

from excars import app
from excars.db import database, get_models


@pytest.fixture(scope='session')
def db():
    _drop_test_database()
    _create_test_database()

    connection_params = db_url.parse(app.application.config.DATABASE_URL)
    connection_params['database'] = _get_test_database_name()

    test_db = database.__class__(**connection_params)
    init_social(app.application, test_db)

    models = get_models(app.application)
    test_db.bind(models, bind_refs=False, bind_backrefs=False)

    with test_db:
        test_db.create_tables(models)

    yield test_db

    with test_db:
        test_db.drop_tables(models)

    _drop_test_database()


@pytest.fixture(scope='function')
def transaction(db):
    with db.transaction() as txn:
        yield txn
        txn.rollback()


@pytest.fixture(autouse=True)
def _require_db_marker(request):
    marker = request.node.get_closest_marker('require_db')
    if marker:
        return request.getfixturevalue('transaction')
    return None


def _create_test_database():
    _execute_sql('CREATE DATABASE %s ;' % _get_test_database_name())


def _drop_test_database():
    _execute_sql('DROP DATABASE IF EXISTS %s ;' % _get_test_database_name())


def _execute_sql(query, values=None):
    conn_params = db_url.parse(app.application.config.DATABASE_URL)

    conn = psycopg2.connect(
        user=conn_params['user'],
        password=conn_params['password'],
        host=conn_params['host'],
        port=conn_params['port'],
        dbname=conn_params['database'],
    )

    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    cur = conn.cursor()
    cur.execute(query, values)

    cur.close()
    conn.close()


def _get_test_database_name():
    connection_params = db_url.parse(app.application.config.DATABASE_URL)
    return f'{connection_params["database"]}_test'
