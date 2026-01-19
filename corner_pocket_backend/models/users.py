from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
    from .stats import Stat


class User(Base):
    """A player in the pool hall.

    Represents someone who can challenge others to matches, track their
    wins/losses, and generally hustle around the virtual felt. Each user
    has a unique email and handle for identification.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)  # For login and contact
    handle: Mapped[str] = mapped_column(
        String, unique=True, nullable=False
    )  # Public display name/username
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )  # When they joined the hall
    password_hash: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )  # For authentication
    stats: Mapped[List["Stat"]] = relationship(
        "Stat", back_populates="user", cascade="all, delete-orphan"
    )
