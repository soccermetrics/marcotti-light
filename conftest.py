import pytest
from sqlalchemy.orm.session import Session
from sqlalchemy.engine import create_engine

from light.config.local import LocalConfig


class TestConfig(LocalConfig):
    DBNAME = 'test-marcotti-light'


def pytest_addoption(parser):
    parser.addoption('--schema', action='store', default='base', help='Indicate schema to use in test suite')


@pytest.fixture('session')
def config():
    return TestConfig()


@pytest.fixture('session')
def cmdopt(request):
    return request.config.getoption('--schema')


@pytest.fixture(scope='session')
def db_connection(request, config, cmdopt):
    engine = create_engine(config.DATABASE_URI)
    connection = engine.connect()
    if cmdopt == 'club':
        from light.club import ClubSchema
        schema = ClubSchema
    elif cmdopt == 'natl':
        from light.natl import NatlSchema
        schema = NatlSchema
    else:
        from light.common import BaseSchema
        schema = BaseSchema
    schema.metadata.create_all(connection)

    def fin():
        schema.metadata.drop_all(connection)
        connection.close()
        engine.dispose()
    request.addfinalizer(fin)
    return connection


@pytest.fixture()
def session(request, db_connection):
    __transaction = db_connection.begin_nested()
    session = Session(db_connection)

    def fin():
        session.close()
        __transaction.rollback()
    request.addfinalizer(fin)
    return session
