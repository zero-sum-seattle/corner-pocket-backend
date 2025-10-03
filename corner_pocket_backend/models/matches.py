from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from .base import Base
from .games import GameType



class MatchStatus(str, Enum):
    """The status of a match."""
    PENDING = "PENDING"      # Creator is adding games, not ready for approval
    APPROVED = "APPROVED"    # Opponent approved, match is official 
    DECLINED = "DECLINED"    # Opponent said "nah, that didn't happen"
    CANCELLED = "CANCELLED"  # Creator cancelled the match

class Match(Base):
    """A pool match between two players.
    
    Represents a series of games (racks) played between a creator and opponent.
    Goes through a lifecycle: creator adds games → submits for approval → 
    opponent approves/declines. Only approved matches count toward stats.
    """
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey("users.id"))  # Who initiated the match
    opponent_id = Column(Integer, ForeignKey("users.id"))  # Who they're playing against
    game_type = Column(SQLEnum(GameType), nullable=False)
    race_to = Column(Integer, nullable=False)
    status = Column(
        SQLEnum(MatchStatus),
        nullable=False,
        default=MatchStatus.PENDING,
    )  # Status of the match

    # Relationships give you easy access to related objects
    creator = relationship("User", foreign_keys=[creator_id])
    opponent = relationship("User", foreign_keys=[opponent_id])
    games = relationship("Game", back_populates="match")  # All racks in this match
    approval = relationship("Approval", back_populates="match", uselist=False)  # Approval of the match
