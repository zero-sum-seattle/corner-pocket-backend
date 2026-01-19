from datetime import datetime, timedelta

from corner_pocket_backend.models.users import User
from corner_pocket_backend.services.security import SecurityDbService


class TestSecurityDbService:
    def test_create_refresh_token(self, db_session):
        svc = SecurityDbService(db=db_session)
        user = User(
            email="test@example.com",
            handle="testuser",
            display_name="Test User",
            password_hash="not_a_hash_lolz",
        )
        db_session.add(user)
        db_session.commit()

        refresh_token_hash = "not_a_token_hash_lolz"  # mock hash
        expires_at = datetime.utcnow() + timedelta(days=30)

        refresh_token = svc.store_refresh_token(
            user_id=user.id, token_hash=refresh_token_hash, expires_at=expires_at
        )

        assert refresh_token.id is not None
        assert refresh_token.user_id == user.id
        assert refresh_token.token_hash == refresh_token_hash
        assert refresh_token.expires_at is not None
        assert refresh_token.revoked_at is None

    def test_get_refresh_token(self, db_session):
        svc = SecurityDbService(db=db_session)
        user = User(
            email="test@example.com",
            handle="testuser",
            display_name="Test User",
            password_hash="not_a_hash_lolz",
        )

        db_session.add(user)
        db_session.commit()

        refresh_token_hash = "not_a_token_hash_lolz"
        expires_at = datetime.utcnow() + timedelta(days=30)
        refresh_token = svc.store_refresh_token(
            user_id=user.id, token_hash=refresh_token_hash, expires_at=expires_at
        )

        fetched = svc.get_refresh_token(refresh_token_hash)

        assert fetched is not None
        assert fetched.id == refresh_token.id
        assert fetched.user_id == user.id
        assert fetched.token_hash == refresh_token_hash
        assert fetched.expires_at == expires_at
        assert fetched.revoked_at is None

    def test_verify_refresh_token(self, db_session):
        svc = SecurityDbService(db=db_session)
        user = User(
            email="test@example.com",
            handle="testuser",
            display_name="Test User",
            password_hash="not_a_hash_lolz",
        )
        db_session.add(user)
        db_session.commit()

        refresh_token_hash = "not_a_token_hash_lolz"
        expires_at = datetime.utcnow() + timedelta(days=30)
        svc.store_refresh_token(
            user_id=user.id, token_hash=refresh_token_hash, expires_at=expires_at
        )

        verified = svc.verify_refresh_token(refresh_token_hash)
        assert verified is True

    def test_revoke_refresh_token(self, db_session):
        svc = SecurityDbService(db=db_session)
        user = User(
            email="test@example.com",
            handle="testuser",
            display_name="Test User",
            password_hash="not_a_hash_lolz",
        )
        db_session.add(user)
        db_session.commit()

        refresh_token_hash = "not_a_token_hash_lolz"
        expires_at = datetime.utcnow() + timedelta(days=30)
        svc.store_refresh_token(
            user_id=user.id, token_hash=refresh_token_hash, expires_at=expires_at
        )

        svc.revoke_refresh_token(refresh_token_hash)
        revoked = svc.verify_refresh_token(refresh_token_hash)
        assert revoked is False

    def test_delete_refresh_token(self, db_session):
        svc = SecurityDbService(db=db_session)
        user = User(
            email="test@example.com",
            handle="testuser",
            display_name="Test User",
            password_hash="not_a_hash_lolz",
        )
        db_session.add(user)
        db_session.commit()

        refresh_token_hash = "not_a_token_hash_lolz"
        expires_at = datetime.utcnow() + timedelta(days=30)
        svc.store_refresh_token(
            user_id=user.id, token_hash=refresh_token_hash, expires_at=expires_at
        )

        svc.delete_refresh_token(refresh_token_hash)
        deleted = svc.get_refresh_token(refresh_token_hash)
        assert deleted is None
