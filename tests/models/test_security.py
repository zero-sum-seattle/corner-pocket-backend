from corner_pocket_backend.models.security import RefreshToken
from corner_pocket_backend.models.users import User
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from corner_pocket_backend.models import Base
import pytest


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_refresh_token(db_session):
    user = User(email="test@example.com", handle="testuser", display_name="Test User")
    db_session.add(user)
    db_session.commit()

    refresh_token = RefreshToken(
        user_id=user.id,
        token_hash="test_token_hash",
        expires_at=datetime.now() + timedelta(days=30),
    )
    db_session.add(refresh_token)
    db_session.commit()

    assert refresh_token.id is not None
    assert refresh_token.user_id == user.id
    assert refresh_token.token_hash == "test_token_hash"
    assert refresh_token.revoked_at is None
