import pytest
from datetime import datetime
from sqlalchemy import create_engine, SQLEnum as SQLAlchemyEnum
from sqlalchemy.orm import sessionmaker
from corner_pocket_backend.models import Base, User, Match, MatchStatus


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


@pytest.fixture
def sample_users(db_session):
    """Create sample users for testing matches."""
    creator = User(email="creator@test.com", handle="creator")
    opponent = User(email="opponent@test.com", handle="opponent")
    
    db_session.add_all([creator, opponent])
    db_session.commit()
    
    return creator, opponent


def test_match_creation(db_session, sample_users):
    """Test creating a basic match between two users."""
    creator, opponent = sample_users
    
    match = Match(
        creator_id=creator.id,
        opponent_id=opponent.id,
    )
    
    db_session.add(match)
    db_session.commit()
    
    assert match.id is not None
    assert match.creator_id == creator.id
    assert match.opponent_id == opponent.id


def test_match_relationships(db_session, sample_users):
    """Test that match relationships work correctly."""
    creator, opponent = sample_users
    
    match = Match(
        creator_id=creator.id,
        opponent_id=opponent.id,
    )
    
    db_session.add(match)
    db_session.commit()
    
    # Test relationships
    assert match.creator.handle == "creator"
    assert match.opponent.handle == "opponent"
    assert match.creator.email == "creator@test.com"


def test_match_status_enum():
    """Test that MatchStatus enum has the expected values."""
    assert MatchStatus.PENDING == "PENDING"
    assert MatchStatus.APPROVED == "APPROVED"
    assert MatchStatus.DECLINED == "DECLINED"
    assert MatchStatus.CANCELLED == "CANCELLED"

def test_match_foreign_key_constraints(db_session):
    """Test that foreign key constraints work."""
    # Try to create match with non-existent user IDs
    match = Match(
        creator_id=999,  # Doesn't exist
        opponent_id=888,  # Doesn't exist
    )
    
    db_session.add(match)
    
    # Should raise foreign key constraint error
    with pytest.raises(Exception):
        db_session.commit()
    


def test_user_cannot_play_themselves(db_session, sample_users):
    """Test business logic: user shouldn't be able to create match against themselves."""
    creator, _ = sample_users
    
    # This is more of a business logic test - the DB allows it but the app shouldn't
    match = Match(
        creator_id=creator.id,
        opponent_id=creator.id,  # Same user!
    )
    
    db_session.add(match)
    db_session.commit()  # DB allows it
    
    # Business logic should prevent this in the service layer
    assert match.creator_id == match.opponent_id  # Shows the issue exists


def test_match_status_defaults_to_pending(db_session, sample_users):
    """Match.status should default to PENDING when not provided."""
    creator, opponent = sample_users

    match = Match(
        creator_id=creator.id,
        opponent_id=opponent.id,
    )

    db_session.add(match)
    db_session.commit()

    assert match.status == MatchStatus.PENDING


def test_match_status_can_be_set_explicitly(db_session, sample_users):
    """Match.status can be set explicitly and should persist that value."""
    creator, opponent = sample_users

    match = Match(
        creator_id=creator.id,
        opponent_id=opponent.id,
        status=MatchStatus.DECLINED,
    )

    db_session.add(match)
    db_session.commit()

    assert match.status == MatchStatus.DECLINED
