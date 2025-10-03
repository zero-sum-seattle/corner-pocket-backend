import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from corner_pocket_backend.models import Base


@pytest.fixture
def db_session():
    """Provide a fresh in-memory SQLite DB session per test.

    Enables foreign keys to mirror Postgres behavior for relational tests.
    """
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


