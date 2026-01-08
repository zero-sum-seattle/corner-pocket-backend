from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from corner_pocket_backend.models import User
from corner_pocket_backend.core.password import verify_password


class UsersDbService:
    """Service for managing users in the database.

    Provides CRUD operations for user accounts including creation,
    lookup, authentication, and profile updates.

    Args:
        db: SQLAlchemy database session for executing queries.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, email: str, handle: str, display_name: str, password_hash: str) -> User:
        """Create a new user (uncommitted).

        Args:
            email: User's email address (must be unique).
            handle: User's public username/handle (must be unique).
            display_name: User's display name shown in the UI.

        Returns:
            The newly created User object (flushed but not committed).

        Raises:
            ValueError: If a user with the given email or handle already exists.
        """
        user = User(
            email=email, handle=handle, display_name=display_name, password_hash=password_hash
        )
        self.db.add(user)
        try:
            self.db.flush()
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError("User with this email or handle already exists") from e
        return user

    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email.

        Args:
            email: The email address to search for.

        Returns:
            The User if found, None otherwise.
        """
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID.

        Args:
            user_id: The primary key ID of the user.

        Returns:
            The User if found, None otherwise.
        """
        return self.db.get(User, user_id)

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password.

        Args:
            email: The user's email address.
            password: The plaintext password to verify.

        Returns:
            The User if credentials are valid, None otherwise.

        Note:
            Currently a stub - password validation not implemented yet.
        """
        user = self.get_by_email(email)
        if not user:
            return None
        if not user.password_hash:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def delete_user(self, user_id: int) -> User:
        """Delete a user from the database.

        Args:
            user_id: The primary key ID of the user to delete.

        Returns:
            The deleted User object.

        Raises:
            ValueError: If no user with the given ID exists.
        """
        user = self.db.get(User, user_id)
        if not user:
            raise ValueError("user not found")
        self.db.delete(user)
        self.db.flush()
        return user

    def edit_user(
        self,
        user_id: int,
        email: Optional[str] = None,
        handle: Optional[str] = None,
        display_name: Optional[str] = None,
    ) -> User:
        """Edit a user's profile in the database.

        Args:
            user_id: The primary key ID of the user to edit.
            email: New email address (optional, must be unique if provided).
            handle: New handle/username (optional, must be unique if provided).
            display_name: New display name (optional).

        Returns:
            The updated User object.

        Raises:
            ValueError: If no user with the given ID exists, or if the new
                email/handle conflicts with an existing user.
        """
        user = self.db.get(User, user_id)
        if not user:
            raise ValueError("user not found")
        if email is not None:
            user.email = email
        if handle is not None:
            user.handle = handle
        if display_name is not None:
            user.display_name = display_name
        try:
            self.db.flush()
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError("User with this email or handle already exists") from e
        return user
