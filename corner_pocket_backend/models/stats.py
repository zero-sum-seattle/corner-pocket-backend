from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import Integer, DateTime, func, ForeignKey, Enum as SQLEnum, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .games import GameType

if TYPE_CHECKING:
    from .users import User


class Stat(Base):
    """Persisted user stats for a game type and time period.

    Stores all-time stats when period fields are null, and monthly stats
    when period_start/period_end are set to the bucket window.
    """

    __tablename__ = "stats"
    __table_args__ = (
        Index(
            "uq_stats_all_time",
            "user_id", "game_type",
            unique=True,
            postgresql_where=text("period_start IS NULL AND period_end IS NULL"),
        ),
        Index(
            "uq_stats_period",
            "user_id", "game_type", "period_start", "period_end",
            unique=True,
            postgresql_where=text("period_start IS NOT NULL AND period_end IS NOT NULL"),
        )
        
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    game_type: Mapped[GameType] = mapped_column(SQLEnum(GameType), nullable=False)
    period_start: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    period_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    matches_played: Mapped[int] = mapped_column(Integer, nullable=False)
    wins: Mapped[int] = mapped_column(Integer, nullable=False)
    losses: Mapped[int] = mapped_column(Integer, nullable=False)
    racks_won: Mapped[int] = mapped_column(Integer, nullable=False)
    racks_lost: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])
