from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

# NOTE: Replace with real DB impl. This is a stub so routes run.
USERS = {}
PASSWORDS = {}

@dataclass
class User:
    id: str
    email: str
    handle: str
    display_name: str

class UsersService:
    def register(self, email: str, handle: str, display_name: str, password: str) -> None:
        uid = str(uuid4())
        USERS[email] = User(id=uid, email=email, handle=handle, display_name=display_name)
        PASSWORDS[email] = password

    def authenticate(self, email: str, password: str) -> Optional[User]:
        if email in USERS and PASSWORDS.get(email) == password:
            return USERS[email]
        return None

    def get_user(self, user_id: str) -> Optional[User]:
        for u in USERS.values():
            if u.id == user_id:
                return u
        return None

    def require_user(self):
        # This is wired by core.security.get_current_user in real impl
        # For now, just return the first user to let you boot UI against it.
        return next(iter(USERS.values()), None)
