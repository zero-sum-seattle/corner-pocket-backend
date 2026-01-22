import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from corner_pocket_backend.main import corner_pocket_backend
from corner_pocket_backend.models import Base  # Import models to register with Base
from corner_pocket_backend.core.db import get_db
from corner_pocket_backend.models.users import User
from corner_pocket_backend.core.password import get_password_hash


@pytest.fixture
def db_session():
    """Provide a fresh in-memory SQLite DB session per test.

    Enables foreign keys to mirror Postgres behavior for relational tests.
    Uses StaticPool to ensure all connections share the same in-memory database.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Ensures same connection is reused (required for in-memory SQLite)
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session):
    """Provide a test client with a database session override."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    corner_pocket_backend.dependency_overrides[get_db] = override_get_db

    with TestClient(corner_pocket_backend) as test_client:
        yield test_client

    corner_pocket_backend.dependency_overrides.clear()


@pytest.fixture
def create_user(
    db_session: Session, username: str = "testuser", password: str = "securepassword123"
):
    """Create a user and return the user object."""
    user = User(
        email=f"{username}@example.com",
        handle=username,
        display_name=f"Test User {username}",
        password_hash=get_password_hash(password),
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def login_user(client: TestClient, create_user: User):
    """Login a user and return the access token."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": create_user.email, "password": "securepassword123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]
