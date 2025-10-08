from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey, func, Enum as SQLEnum
from enum import Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .base import Base
from .matches import Match


class RaceTo(Enum):
    """Common race-to targets for pool matches."""

    THREE = 3  # Quick match
    FIVE = 5  # Standard casual play
    SEVEN = 7  # Serious business
    NINE = 9  # Tournament style
    THIRTEEN = 13  # Long session
    FIFTEEN = 15  # All day affair


class GameType(str, Enum):
    """Types of pool games supported."""

    EIGHT_BALL = "EIGHT_BALL"  # Classic bar room game
    NINE_BALL = "NINE_BALL"  # Fast-paced rotation
    TEN_BALL = "TEN_BALL"  # Called-shot rotation


class Game(Base):
    """An individual rack/game within a match.

    Represents one completed game where someone sank the money ball.
    Multiple games make up a match. Tracks who won, what type of game
    it was, and when it happened.
    """

    __tablename__ = "games"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    match_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("matches.id"), nullable=False
    )  # Which match this belongs to
    game_type: Mapped[GameType] = mapped_column(
        SQLEnum(GameType), nullable=False
    )  # 8-ball, 9-ball, etc.
    winner_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )  # Who sank the money ball
    loser_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )  # Who got schooled
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )  # When this rack was completed
    frame_number: Mapped[int] = mapped_column(
        Integer, nullable=True
    )  # Which frame this is (can be added later)

    match: Mapped[Match] = relationship("Match", back_populates="games")
