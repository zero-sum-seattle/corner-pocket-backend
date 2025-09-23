from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from corner_pocket_backend.core.security import create_access_token, get_current_user
from corner_pocket_backend.services.users import UsersService

router = APIRouter()

class RegisterIn(BaseModel):
    email: str
    handle: str
    display_name: str
    password: str

class LoginIn(BaseModel):
    email: str
    password: str

@router.post("/auth/register")
def register(data: RegisterIn):
    UsersService().register(email=data.email, handle=data.handle, display_name=data.display_name, password=data.password)
    return {"ok": True}

@router.post("/auth/login")
def login(data: LoginIn):
    user = UsersService().authenticate(email=data.email, password=data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def me(user=Depends(get_current_user)):
    return user
