import pytest
from excars import app
from excars.db import get_models


@pytest.fixture(scope='session')
def db():
    models = get_models(app.app)

    test_db = app.db.__class__(
        f'{app.db.database}_test',
        **app.db.connect_params
    )

    test_db.bind(models, bind_refs=False, bind_backrefs=False)

    with test_db:
        test_db.create_tables(models)

    yield test_db

    with test_db:
        test_db.drop_tables(models)


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
