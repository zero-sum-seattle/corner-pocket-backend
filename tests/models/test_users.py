import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from corner_pocket_backend.models.users import User, Base


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_user_creation(db_session):
    """Test creating a basic user."""
    user = User(
        email="test@poolhall.com",
        handle="pool_shark",
    )
    
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.email == "test@poolhall.com"
    assert user.handle == "pool_shark"
    assert isinstance(user.created_at, datetime)


def test_user_unique_constraints(db_session):
    """Test that email and handle must be unique."""
    user1 = User(email="test@test.com", handle="player1")
    user2 = User(email="test@test.com", handle="player2")  # Same email
    
    db_session.add(user1)
    db_session.commit()
    
    db_session.add(user2)
    
    # Should raise an integrity error due to unique constraint
    with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
        db_session.commit()


def test_user_handle_uniqueness(db_session):
    """Test that handles must be unique."""
    user1 = User(email="first@test.com", handle="samename")
    user2 = User(email="second@test.com", handle="samename")  # Same handle
    
    db_session.add(user1)
    db_session.commit()
    
    db_session.add(user2)
    
    with pytest.raises(Exception):
        db_session.commit()


def test_user_required_fields(db_session):
    """Test that required fields cannot be None."""
    # Should fail without email
    user = User(handle="test_handle")
    db_session.add(user)
    
    with pytest.raises(Exception):
        db_session.commit()


def test_user_handle_required(db_session):
    """Test that handle is required (cannot be None)."""
    user = User(email="nohandle@test.com")
    db_session.add(user)
    with pytest.raises(Exception):
        db_session.commit()
