import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from corner_pocket_backend.models import Base, User, GameType, Stat
from datetime import datetime


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")

    from sqlalchemy import event

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_stat_creation(db_session):
    """Test creating a basic stat."""
    user = User(email="test@poolhall.com", handle="testuser", display_name="Test User")
    db_session.add(user)
    db_session.commit()

    stat = Stat(
        user_id=user.id,
        game_type=GameType.EIGHT_BALL,
        period_start=None,
        period_end=None,
        matches_played=0,
        wins=0,
        losses=0,
        racks_won=0,
        racks_lost=0,
    )
    db_session.add(stat)
    db_session.commit()

    assert stat.id is not None
    assert stat.user_id == user.id
    assert stat.game_type == GameType.EIGHT_BALL


def test_stat_unique_constraints(db_session):
    """Test that stat must be unique per user and game type."""
    user = User(email="test@poolhall.com", handle="testuser", display_name="Test User")
    db_session.add(user)
    db_session.commit()

    stat = Stat(
        user_id=user.id,
        game_type=GameType.EIGHT_BALL,
        period_start=None,
        period_end=None,
        matches_played=0,
        wins=0,
        losses=0,
        racks_won=0,
        racks_lost=0,
    )
    db_session.add(stat)
    db_session.commit()

    stat2 = Stat(
        user_id=user.id,
        game_type=GameType.EIGHT_BALL,
        period_start=None,
        period_end=None,
        matches_played=0,
        wins=0,
        losses=0,
        racks_won=0,
        racks_lost=0,
    )
    db_session.add(stat2)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_stat_period_constraints(db_session):
    """Test that stat must be unique per user and game type."""
    user = User(email="test@poolhall.com", handle="testuser", display_name="Test User")
    db_session.add(user)
    db_session.commit()

    stat = Stat(
        user_id=user.id,
        game_type=GameType.EIGHT_BALL,
        period_start=datetime.now(),
        period_end=datetime.now(),
        matches_played=0,
        wins=0,
        losses=0,
        racks_won=0,
        racks_lost=0,
    )
    db_session.add(stat)
    db_session.commit()

    stat2 = Stat(
        user_id=user.id,
        game_type=GameType.EIGHT_BALL,
        period_start=datetime.now(),
        period_end=datetime.now(),
        matches_played=0,
        wins=0,
        losses=0,
        racks_won=0,
        racks_lost=0,
    )
    db_session.add(stat2)
    with pytest.raises(IntegrityError):
        db_session.commit()
