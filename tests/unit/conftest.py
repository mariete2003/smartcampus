import pytest

from app.database import connect, init_db


@pytest.fixture
def conn():
    """Base de datos SQLite en memoria, nueva para cada test."""
    connection = connect(":memory:")
    init_db(connection)
    yield connection
    connection.close()
