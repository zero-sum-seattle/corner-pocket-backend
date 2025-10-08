from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from enum import Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import Base
from .matches import Match
from .users import User


class ApprovalStatus(str, Enum):
    """The status of an approval."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"


class Approval(Base):
    """Approval of a match by an opponent."""

    __tablename__ = "approvals"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(Integer, ForeignKey("matches.id"), nullable=False, unique=True)
    match: Mapped[Match] = relationship("Match", back_populates="approval")
    approver_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    approver: Mapped[User] = relationship("User", foreign_keys=[approver_user_id])
    status: Mapped[ApprovalStatus] = mapped_column(SQLEnum(ApprovalStatus), nullable=False, default=ApprovalStatus.PENDING)
    note: Mapped[str] = mapped_column(String)
    decided_at: Mapped[datetime] = mapped_column(DateTime)
