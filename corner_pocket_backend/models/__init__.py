from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func
from typing import Optional
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[Optional["datetime"]] = mapped_column(DateTime(timezone=True), server_default=func.now())
