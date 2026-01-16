from typing import TYPE_CHECKING, List
from sqlalchemy import Integer, ForeignKey, String, DateTime, func,Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import Base
from datetime import datetime





class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    expired_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)