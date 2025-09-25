from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from .base import Base



class MatchStatus(str, Enum):
    """The lifecycle of a match between two players."""
    PENDING = "PENDING"      # Creator is adding games, not ready for approval
    SUBMITTED = "SUBMITTED"  # Creator submitted for opponent approval
    APPROVED = "APPROVED"    # Opponent approved, match is official 
    DECLINED = "DECLINED"    # Opponent said "nah, that didn't happen"

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
    
    # Relationships give you easy access to related objects
    creator = relationship("User", foreign_keys=[creator_id])
    opponent = relationship("User", foreign_keys=[opponent_id])
    games = relationship("Game", back_populates="match")  # All racks in this match