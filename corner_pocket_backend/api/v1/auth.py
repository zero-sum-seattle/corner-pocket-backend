from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from corner_pocket_backend.core.security import get_current_user, create_access_token
from corner_pocket_backend.core.password import get_password_hash
from corner_pocket_backend.models.users import User
from corner_pocket_backend.services.users import UsersDbService
from corner_pocket_backend.core.db import get_db
from datetime import datetime
from typing import Any

router = APIRouter()


class RegisterIn(BaseModel):
    email: EmailStr
    handle: str
    display_name: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    handle: str
    display_name: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/auth/register")
def register(data: RegisterIn, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Create a new user account.

    Accepts basic registration fields and delegates to UsersService to
    create the user record. Returns a simple success payload on completion.
    """
    try:
        password_hash = get_password_hash(data.password)
        user = UsersDbService(db).create(
            email=data.email,
            handle=data.handle,
            display_name=data.display_name,
            password_hash=password_hash,
        )
        token = create_access_token({"sub": str(user.id)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"ok": True, "user_id": user.id, "access_token": token, "token_type": "bearer"}


@router.post("/auth/login")
def login(data: LoginIn, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Authenticate a user and issue a JWT access token.

    Verifies email/password, then returns a bearer token encoded with the
    user's id as the subject ("sub"). The token is used for protected APIs.
    """
    try:
        user = UsersDbService(db).authenticate(email=data.email, password=data.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})

    return {"user_id": user.id, "access_token": token, "token_type": "bearer"}


@router.get("/auth/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    """Return the authenticated user's profile.

    Uses the get_current_user dependency to validate the bearer token and
    return the current user's data.
    """

    return UserOut.model_validate(user)
