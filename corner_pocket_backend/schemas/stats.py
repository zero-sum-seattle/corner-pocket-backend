from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from corner_pocket_backend.models.games import GameType


class StatOut(BaseModel):
    """Public schema for persisted user stats."""

    id: int
    user_id: int
    game_type: GameType
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    matches_played: int
    wins: int
    losses: int
    racks_won: int
    racks_lost: int
    updated_at: datetime

    class Config:
        from_attributes = True
