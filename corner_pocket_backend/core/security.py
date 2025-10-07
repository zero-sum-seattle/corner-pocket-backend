from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from corner_pocket_backend.core.config import settings
from corner_pocket_backend.services.users import UsersDbService

"""Security utilities for JWT creation and authentication dependencies.

This module provides helpers to issue access tokens and a FastAPI dependency
to authenticate requests using the Authorization: Bearer <token> header.
"""

ALGO = "HS256"
bearer = HTTPBearer(auto_error=False)

def create_access_token(payload: dict, expires_minutes: int = 60*24) -> str:
    """Create a signed JWT access token.

    Args:
        payload: Claims to embed in the token. Should include a subject ("sub").
        expires_minutes: Token lifetime in minutes. Defaults to 24 hours.

    Returns:
        A compact JWT string signed with the configured secret.
    """
    to_encode = payload.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGO)

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    """Validate the bearer token and return the authenticated user.

    This dependency extracts the token from the Authorization header, verifies
    its signature and expiry, looks up the user by subject, and returns the
    user object. It raises 401 for any authentication failure.

    Args:
        creds: Parsed Authorization header provided by HTTPBearer.

    Returns:
        The authenticated user object from UsersService.
    """
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        data = jwt.decode(creds.credentials, settings.JWT_SECRET, algorithms=[ALGO])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    uid = data.get("sub")
    user = UsersDbService().get_user(uid)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user
