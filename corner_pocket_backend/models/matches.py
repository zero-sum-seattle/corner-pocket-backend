from sqlalchemy import Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from enum import Enum
from .base import Base
from .games import GameType, Game
from .users import User
from typing import List
from .approvals import Approval



class MatchStatus(str, Enum):
    """The status of a match."""

    PENDING = "PENDING"  # Creator is adding games, not ready for approval
    APPROVED = "APPROVED"  # Opponent approved, match is official
    DECLINED = "DECLINED"  # Opponent said "nah, that didn't happen"
    CANCELLED = "CANCELLED"  # Creator cancelled the match


class Match(Base):
    """A pool match between two players.

    Represents a series of games (racks) played between a creator and opponent.
    Goes through a lifecycle: creator adds games → submits for approval →
    opponent approves/declines. Only approved matches count toward stats.
    """

    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    creator_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))  # Who initiated the match
    opponent_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))  # Who they're playing against
    game_type: Mapped[GameType] = mapped_column(SQLEnum(GameType), nullable=False)
    race_to: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[MatchStatus] = mapped_column(
        SQLEnum(MatchStatus),
        nullable=False,
        default=MatchStatus.PENDING,
    )  # Status of the match

    # Relationships give you easy access to related objects
    creator: Mapped[User] = relationship("User", foreign_keys=[creator_id])
    opponent: Mapped[User] = relationship("User", foreign_keys=[opponent_id])
    games: Mapped[List[Game]] = relationship("Game", back_populates="match")  # All racks in this match
    approval: Mapped[Approval] = relationship(
        "Approval", back_populates="match", uselist=False
    )  # Approval of the match
