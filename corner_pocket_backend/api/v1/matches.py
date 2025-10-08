from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import Optional
from corner_pocket_backend.schemas.common import GameType
from corner_pocket_backend.core.security import get_current_user
from corner_pocket_backend.models.users import User

router = APIRouter()


class MatchCreate(BaseModel):
    """Create a new match with an opponent."""

    opponent_id: int
    game_type: GameType
    race_to: Optional[int] = None


class GameAdd(BaseModel):
    """Add a game result to a pending match."""

    winner_user_id: int


@router.post("/matches")
def create_match(payload: MatchCreate, user: User = Depends(get_current_user)) -> None:
    """Create a new match with an opponent.

    The authenticated user becomes the creator. Supports optional race-to
    target and game type selection.
    """
    pass


@router.get("/matches")
def list_matches(
    mine: bool = Query(True), status: Optional[str] = None, user: User = Depends(get_current_user)
) -> None:
    """List matches, defaulting to those involving the current user.

    Pass mine=false to view all matches. Filter by status when provided.
    """
    pass


@router.get("/matches/{match_id}")
def get_match(match_id: str, user: User = Depends(get_current_user)) -> None:
    """Fetch a specific match, including its games, if the user participates."""
    pass


@router.post("/matches/{match_id}/games")
def add_game(match_id: str, payload: GameAdd, user: User = Depends(get_current_user)) -> None:
    """Append a game result to a pending match by specifying the winner."""
    pass


@router.post("/matches/{match_id}/submit")
def submit(match_id: str, user: User = Depends(get_current_user)) -> None:
    """Submit a pending match for opponent approval (creator only)."""
    pass


@router.post("/matches/{match_id}/approve")
def approve(match_id: str, user: User = Depends(get_current_user)) -> None:
    """Approve a submitted match (opponent only)."""
    pass


@router.post("/matches/{match_id}/decline")
def decline(match_id: str, user: User = Depends(get_current_user)) -> None:
    """Decline a submitted match (opponent only)."""
    pass
