from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from corner_pocket_backend.models.security import RefreshToken
from corner_pocket_backend.core.security import REFRESH_TOKEN_EXPIRES_DAYS


class SecurityDbService:
    """Service for managing security tokens in the database.

    Provides CRUD operations for refresh tokens including creation, lookup, and verification.
    """

    def __init__(self, db: Session):
        self.db = db

    def store_refresh_token(
        self, user_id: int, token_hash: str, expires_at: Optional[datetime] = None
    ) -> RefreshToken:
        """Create a new refresh token.

        Args:
            user_id: The ID of the user associated with the token.
            token_hash: The hash of the token.
            expires_at: When the token expires (defaults to now + REFRESH_TOKEN_EXPIRES_DAYS).
        """
        if expires_at is None:
            expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRES_DAYS)
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(refresh_token)
        self.db.flush()
        return refresh_token

    def get_refresh_token(self, token_hash: str) -> Optional[RefreshToken]:
        """Get a refresh token by its hash.

        Args:
            token_hash: The hash of the token.
        """
        return self.db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

    def verify_refresh_token(self, token_hash: str) -> bool:
        """Verify a refresh token.

        Args:
            token_hash: The hash of the token.
        """
        refresh_token = self.get_refresh_token(token_hash)
        if not refresh_token:
            return False
        if refresh_token.revoked_at is not None:
            return False
        if refresh_token.expires_at < datetime.utcnow():
            return False
        return True

    def revoke_refresh_token(self, token_hash: str) -> None:
        """Revoke a refresh token."""
        refresh_token = self.get_refresh_token(token_hash)
        if not refresh_token:
            return
        refresh_token.revoked_at = datetime.utcnow()
        self.db.flush()

    def delete_refresh_token(self, token_hash: str) -> None:
        """Delete a refresh token.

        Args:
            token_hash: The hash of the token.
        """
        self.db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).delete()
        self.db.commit()
