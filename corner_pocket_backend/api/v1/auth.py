from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from corner_pocket_backend.core.security import (
    get_current_user,
    create_access_token,
    create_refresh_token,
)
from corner_pocket_backend.core.password import get_password_hash
from corner_pocket_backend.models.users import User
from corner_pocket_backend.services.users import UsersDbService
from corner_pocket_backend.services.security import SecurityDbService
from corner_pocket_backend.core.db import get_db
from typing import Any
from corner_pocket_backend.schemas.auth import RegisterIn, LoginIn, UserOut, RefreshIn

router = APIRouter()


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
        refresh_token = create_refresh_token({"sub": str(user.id)})
        security_db_service = SecurityDbService(db)
        security_db_service.store_refresh_token(user_id=user.id, token_hash=refresh_token)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "ok": True,
        "user_id": user.id,
        "access_token": token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/auth/refresh")
def refresh(data: RefreshIn, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Refresh a JWT access token.

    Verifies a refresh token and issues a new access token.
    """

    try:
        security_db_service = SecurityDbService(db)
        refresh_token = security_db_service.get_refresh_token(data.refresh_token)
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        if not security_db_service.verify_refresh_token(refresh_token.token_hash):
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except HTTPException as e:
        raise HTTPException(status_code=400, detail=str(e))

    token = create_access_token({"sub": str(refresh_token.user_id)})
    # remove refresh_token
    security_db_service.delete_refresh_token(refresh_token.token_hash)
    # create new refresh_token
    new_refresh_token = create_refresh_token({"sub": str(refresh_token.user_id)})
    security_db_service.store_refresh_token(
        user_id=refresh_token.user_id, token_hash=new_refresh_token
    )

    return {
        "ok": True,
        "access_token": token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


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
    refresh_token = create_refresh_token({"sub": str(user.id)})

    security_db_service = SecurityDbService(db)
    security_db_service.store_refresh_token(user_id=user.id, token_hash=refresh_token)

    return {
        "user_id": user.id,
        "access_token": token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/auth/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    """Return the authenticated user's profile.

    Uses the get_current_user dependency to validate the bearer token and
    return the current user's data.
    """

    return UserOut.model_validate(user)
