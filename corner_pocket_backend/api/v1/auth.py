from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from corner_pocket_backend.core.security import get_current_user
from corner_pocket_backend.models.users import User

router = APIRouter()


class RegisterIn(BaseModel):
    email: EmailStr
    handle: str
    display_name: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


@router.post("/auth/register")
def register(data: RegisterIn) -> None:
    """Create a new user account.

    Accepts basic registration fields and delegates to UsersService to
    create the user record. Returns a simple success payload on completion.
    """
    pass
    # UsersService().register(email=data.email, handle=data.handle, display_name=data.display_name, password=data.password)
    # return {"ok": True}


@router.post("/auth/login")
def login(data: LoginIn) -> None:
    """Authenticate a user and issue a JWT access token.

    Verifies email/password, then returns a bearer token encoded with the
    user's id as the subject ("sub"). The token is used for protected APIs.
    """
    pass
    # user = UsersService().authenticate(email=data.email, password=data.password)
    # if not user:
    #     raise HTTPException(status_code=401, detail="Invalid credentials")
    # token = create_access_token({"sub": str(user.id)})
    # return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def me(user: User = Depends(get_current_user)) -> None:
    """Return the authenticated user's profile.

    Uses the get_current_user dependency to validate the bearer token and
    return the current user's data.
    """
    pass
    # return user
