from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from corner_pocket_backend.models import User


class UsersDbService:
    """Service for managing users."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, email: str, handle: str) -> User:
        """Create a new user (uncommitted)."""
        user = User(email=email, handle=handle)
        self.db.add(user)
        try:
            self.db.flush()
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"User with this email or handle already exists") from e
        return user

    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        return self.db.get(User, user_id)

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user (stub - password validation not implemented yet)."""
        # TODO: implement password hashing and validation
        return self.get_by_email(email)

    def delete_user(self, user_id: int) -> User:
        """Delete a user from the database."""
        user = self.db.get(User, user_id)
        if not user:
            raise ValueError("user not found")
        self.db.delete(user)
        self.db.flush()
        return user
    
    def edit_user(self, user_id: int, email: Optional[str] = None, handle: Optional[str] = None) -> User:
        """Edit a user in the database."""
        user = self.db.get(User, user_id)
        if not user:
            raise ValueError("user not found")
        if email is not None:
            user.email = email
        if handle is not None:
            user.handle = handle
        try:
            self.db.flush()
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"User with this email or handle already exists") from e
        return user
