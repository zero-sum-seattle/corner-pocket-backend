from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from corner_pocket_backend.core.config import settings
from corner_pocket_backend.services.users import UsersService

ALGO = "HS256"
bearer = HTTPBearer(auto_error=False)

def create_access_token(payload: dict, expires_minutes: int = 60*24) -> str:
    to_encode = payload.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGO)

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    if not creds:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        data = jwt.decode(creds.credentials, settings.JWT_SECRET, algorithms=[ALGO])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    uid = data.get("sub")
    user = UsersService().get_user(uid)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user
