"""Tests for authentication API endpoints."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from corner_pocket_backend.services.users import UsersDbService
from corner_pocket_backend.core.security import create_access_token, create_refresh_token
from corner_pocket_backend.core.password import get_password_hash
from corner_pocket_backend.services.security import SecurityDbService


class TestRegister:
    """Tests for POST /api/v1/auth/register endpoint."""

    def test_register_success(self, client: TestClient, db_session: Session):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "handle": "testuser",
                "display_name": "Test User",
                "password": "securepassword123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "user_id" in data
        assert isinstance(data["user_id"], int)

        # Verify user was created in database
        user_service = UsersDbService(db_session)
        user = user_service.get_by_email("test@example.com")
        assert user is not None
        assert user.email == "test@example.com"
        assert user.handle == "testuser"
        assert user.display_name == "Test User"
        assert user.password_hash is not None
        assert user.password_hash != "securepassword123"  # Should be hashed

    def test_register_duplicate_email(self, client: TestClient, db_session: Session):
        """Test registration fails with duplicate email."""
        # Create first user
        user_service = UsersDbService(db_session)
        password_hash = get_password_hash("password123")
        user_service.create(
            email="test@example.com",
            handle="user1",
            display_name="User One",
            password_hash=password_hash,
        )
        db_session.commit()

        # Try to register with same email
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "handle": "user2",
                "display_name": "User Two",
                "password": "password123",
            },
        )

        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    def test_register_duplicate_handle(self, client: TestClient, db_session: Session):
        """Test registration fails with duplicate handle."""
        # Create first user
        user_service = UsersDbService(db_session)
        password_hash = get_password_hash("password123")
        user_service.create(
            email="user1@example.com",
            handle="testuser",
            display_name="User One",
            password_hash=password_hash,
        )
        db_session.commit()

        # Try to register with same handle
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "user2@example.com",
                "handle": "testuser",
                "display_name": "User Two",
                "password": "password123",
            },
        )

        assert response.status_code == 400
        assert "handle" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client: TestClient):
        """Test registration fails with invalid email format."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "not-an-email",
                "handle": "testuser",
                "display_name": "Test User",
                "password": "password123",
            },
        )

        assert response.status_code == 422  # Pydantic validation error

    def test_register_missing_fields(self, client: TestClient):
        """Test registration fails with missing required fields."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                # Missing handle, display_name, password
            },
        )

        assert response.status_code == 422


class TestLogin:
    """Tests for POST /api/v1/auth/login endpoint."""

    def test_login_success(self, client: TestClient, db_session: Session):
        """Test successful login with valid credentials."""
        # Create a user with hashed password
        user_service = UsersDbService(db_session)
        password_hash = get_password_hash("password123")
        user_service.create(
            email="test@example.com",
            handle="testuser",
            display_name="Test User",
            password_hash=password_hash,
        )
        db_session.commit()

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user_id" in data
        assert isinstance(data["user_id"], int)
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
        assert "refresh_token" in data
        assert isinstance(data["refresh_token"], str)
        assert len(data["refresh_token"]) > 0

    def test_login_invalid_email(self, client: TestClient):
        """Test login fails with non-existent email."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 401
        assert "invalid credentials" in response.json()["detail"].lower()

    def test_login_invalid_password(self, client: TestClient, db_session: Session):
        """Test login fails with wrong password."""
        # Create a user
        user_service = UsersDbService(db_session)
        password_hash = get_password_hash("password123")
        user_service.create(
            email="test@example.com",
            handle="testuser",
            display_name="Test User",
            password_hash=password_hash,
        )
        db_session.commit()

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401

    def test_login_missing_fields(self, client: TestClient):
        """Test login fails with missing fields."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                # Missing password
            },
        )

        assert response.status_code == 422


class TestMe:
    """Tests for GET /api/v1/auth/me endpoint."""

    def test_me_success(self, client: TestClient, db_session: Session):
        """Test fetching current user profile with valid token."""
        # Create a user
        user_service = UsersDbService(db_session)
        password_hash = get_password_hash("password123")
        user = user_service.create(
            email="test@example.com",
            handle="testuser",
            display_name="Test User",
            password_hash=password_hash,
        )
        db_session.commit()

        # Generate a valid access token
        token = create_access_token({"sub": str(user.id)})

        # Request with access token
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["email"] == "test@example.com"
        assert data["handle"] == "testuser"
        assert data["display_name"] == "Test User"
        assert "password_hash" not in data  # Should not expose password hash
        assert "created_at" in data

    def test_me_no_token(self, client: TestClient):
        """Test /me fails without authentication token."""
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()

    def test_me_invalid_token(self, client: TestClient):
        """Test /me fails with invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"},
        )

        assert response.status_code == 401
        assert "invalid token" in response.json()["detail"].lower()

    def test_me_expired_token(self, client: TestClient):
        """Test /me fails with expired token."""
        # Create a token that expired (negative expiry)
        token = create_access_token({"sub": "1"}, expires_minutes=-1)

        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401

    def test_me_deleted_user(self, client: TestClient, db_session: Session):
        """Test /me fails if user was deleted after token was issued."""
        # Create a user
        user_service = UsersDbService(db_session)
        password_hash = get_password_hash("password123")
        user = user_service.create(
            email="test@example.com",
            handle="testuser",
            display_name="Test User",
            password_hash=password_hash,
        )
        db_session.commit()

        # Generate token
        token = create_access_token({"sub": str(user.id)})

        # Delete user
        user_service.delete_user(user.id)
        db_session.commit()

        # Try to access /me
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401
        assert "invalid user" in response.json()["detail"].lower()


class TestAuthFlow:
    """Integration tests for complete auth flow."""

    def test_register_login_me_flow(self, client: TestClient):
        """Test complete flow: register → login → access protected endpoint."""
        # 1. Register a new user
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "handle": "newuser",
                "display_name": "New User",
                "password": "securepass123",
            },
        )
        assert register_response.status_code == 200

        # 2. Login with credentials
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "newuser@example.com",
                "password": "securepass123",
            },
        )


        assert login_response.status_code == 200
        data = login_response.json()
        assert "access_token" in data
        assert "user_id" in data
        assert isinstance(data["user_id"], int)
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0
        assert "refresh_token" in data
        assert isinstance(data["refresh_token"], str)
        assert len(data["refresh_token"]) > 0
        # This may fail until authenticate() is fully implemented


        if login_response.status_code == 200:
            token = login_response.json()["access_token"]

            # 3. Access protected endpoint
            me_response = client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert me_response.status_code == 200
            assert me_response.json()["email"] == "newuser@example.com"

class TestRefresh:

    def test_refresh_success(self, client: TestClient, db_session: Session):
        """Test successful refresh of access token."""
        # Create a user
        user_service = UsersDbService(db_session)
        password_hash = get_password_hash("password123")
        user = user_service.create(
            email="test@example.com",
            handle="testuser",
            display_name="Test User",
            password_hash=password_hash,
        )
        db_session.commit()

        # Generate a valid token
        refresh_token = create_refresh_token({"sub": str(user.id)})
        security_db_service = SecurityDbService(db_session)
        security_db_service.store_refresh_token(user_id=user.id, token_hash=refresh_token)

        # Request with token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data