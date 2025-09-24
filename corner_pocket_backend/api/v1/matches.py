from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from corner_pocket_backend.services.users import UsersService
from corner_pocket_backend.services.matches import MatchesService
from corner_pocket_backend.schemas.common import GameType
from corner_pocket_backend.core.security import get_current_user

router = APIRouter()

class MatchCreate(BaseModel):
    opponent_id: str
    game_type: GameType
    race_to: Optional[int] = None

class GameAdd(BaseModel):
    winner_user_id: str

@router.post("/matches")
def create_match(payload: MatchCreate, user=Depends(get_current_user)):
    """Create a new match with an opponent.

    The authenticated user becomes the creator. Supports optional race-to
    target and game type selection.
    """
    return MatchesService().create_match(creator_id=user.id, **payload.model_dump())

@router.get("/matches")
def list_matches(
    mine: bool = Query(True),
    status: Optional[str] = None,
    user=Depends(get_current_user),
):
    """List matches, defaulting to those involving the current user.

    Pass mine=false to view all matches. Filter by status when provided.
    """
    return MatchesService().list_matches(user_id=user.id, mine=mine, status=status)

@router.get("/matches/{match_id}")
def get_match(match_id: str, user=Depends(get_current_user)):
    """Fetch a specific match, including its games, if the user participates."""
    m = MatchesService().get_match(user_id=user.id, match_id=match_id)
    if not m:
        raise HTTPException(status_code=404, detail="Not found")
    return m

@router.post("/matches/{match_id}/games")
def add_game(match_id: str, payload: GameAdd, user=Depends(get_current_user)):
    """Append a game result to a pending match by specifying the winner."""
    return MatchesService().add_game(user_id=user.id, match_id=match_id, winner_user_id=payload.winner_user_id)

@router.post("/matches/{match_id}/submit")
def submit(match_id: str, user=Depends(get_current_user)):
    """Submit a pending match for opponent approval (creator only)."""
    return MatchesService().submit(user_id=user.id, match_id=match_id)

@router.post("/matches/{match_id}/approve")
def approve(match_id: str, user=Depends(get_current_user)):
    """Approve a submitted match (opponent only)."""
    return MatchesService().approve(user_id=user.id, match_id=match_id)

@router.post("/matches/{match_id}/decline")
def decline(match_id: str, user=Depends(get_current_user)):
    """Decline a submitted match (opponent only)."""
    return MatchesService().decline(user_id=user.id, match_id=match_id)
