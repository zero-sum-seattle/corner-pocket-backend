from pydantic import BaseModel, EmailStr
from datetime import datetime


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


class RefreshIn(BaseModel):
    refresh_token: str
