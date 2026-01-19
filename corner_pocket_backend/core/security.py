from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import uuid
from jose import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from corner_pocket_backend.core.config import settings
from corner_pocket_backend.core.db import get_db
from corner_pocket_backend.services.users import UsersDbService
from corner_pocket_backend.models import User

"""Security utilities for JWT creation and authentication dependencies.

This module provides helpers to issue access tokens and a FastAPI dependency
to authenticate requests using the Authorization: Bearer <token> header.
"""

ALGO = "HS256"
bearer = HTTPBearer(auto_error=False)
ACCESS_TOKEN_EXPIRES_MINUTES = 60 * 24
REFRESH_TOKEN_EXPIRES_DAYS = 30
TOKEN_ISSUER = "corner-pocket-backend"
TOKEN_AUDIENCE = "corner-pocket-frontend"
TOKEN_VERSION = "v2"


def _base_claims(token_type: str) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    return {
        "version": TOKEN_VERSION,
        "iat": now,
        "nbf": now,
        "jti": str(uuid.uuid4()),
        "iss": TOKEN_ISSUER,
        "aud": TOKEN_AUDIENCE,
        "token_type": token_type,
    }


def create_access_token(
    payload: Dict[str, Any], expires_minutes: int = ACCESS_TOKEN_EXPIRES_MINUTES
) -> str:
    """Create a signed JWT access token.

    Args:
        payload: Claims to embed in the token. Should include a subject ("sub").
        expires_minutes: Token lifetime in minutes. Defaults to 24 hours.

    Returns:
        A compact JWT string signed with the configured secret.
    """
    if not payload.get("sub"):
        raise ValueError("Access token payload must include 'sub'")
    to_encode = {
        **_base_claims("access"),
        **payload,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=expires_minutes),
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGO)


def create_refresh_token(
    payload: Dict[str, Any], expires_days: int = REFRESH_TOKEN_EXPIRES_DAYS
) -> str:
    """Create a signed JWT refresh token.

    Args:
        payload: Claims to embed in the token. Should include a subject ("sub").
        expires_days: Token lifetime in days. Defaults to 30 days.
    Returns:
        A compact JWT string signed with the configured secret.
    """
    if not payload.get("sub"):
        raise ValueError("Refresh token payload must include 'sub'")
    to_encode = {
        **_base_claims("refresh"),
        **payload,
        "exp": datetime.now(timezone.utc) + timedelta(days=expires_days),
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGO)


def verify_token(token: str, token_type: Optional[str] = None) -> Dict[str, Any]:
    """Verify a JWT token and return the payload.

    Args:
        token: The JWT token to verify.
    Returns:
        The payload of the verified token.
    """
    data = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGO])
    if token_type and data.get("token_type") != token_type:
        raise HTTPException(status_code=401, detail="Invalid token type")
    return data


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)
) -> User:
    """Validate the bearer token and return the authenticated user.

    This dependency extracts the token from the Authorization header, verifies
    its signature and expiry, looks up the user by subject, and returns the
    user object. It raises 401 for any authentication failure.

    Args:
        creds: Parsed Authorization header provided by HTTPBearer.
        db: Database session injected by FastAPI.

    Returns:
        The authenticated user object from UsersDbService.
    """
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        data = verify_token(creds.credentials, token_type="access")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    uid = data.get("sub")
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    try:
        user_id = int(uid)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Token format outdated. Please log in again.")

    user_svc = UsersDbService(db=db)
    user = user_svc.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user
