from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from enum import Enum
from datetime import datetime
from sqlalchemy.orm import relationship
from .base import Base


class ApprovalStatus(str, Enum):
    """The status of an approval."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"

class Approval(Base):
    """Approval of a match by an opponent."""
    __tablename__ = "approvals"
    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, unique=True)
    match = relationship("Match", back_populates="approval")
    approver_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approver = relationship("User", foreign_keys=[approver_user_id])
    status = Column(SQLEnum(ApprovalStatus), nullable=False, default=ApprovalStatus.PENDING)
    note = Column(String)
    decided_at = Column(DateTime)