from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from pydantic import ValidationError

from corner_pocket_backend.core.db import get_db
from corner_pocket_backend.core.security import get_current_user
from corner_pocket_backend.models.games import GameType
from corner_pocket_backend.models.users import User
from corner_pocket_backend.schemas.stats import StatOut
from corner_pocket_backend.services.stats import StatsDbService
from corner_pocket_backend.core.exceptions import CornerPocketError


router = APIRouter()


@router.get("/stats/summary", response_model=list[StatOut])
def summary(
    user_id: int | None = Query(None, description="The user ID to fetch stats for"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[StatOut]:
    """Return a simple summary of results for a user.

    Defaults to the current user. Another user's id may be supplied by query
    for administrative/preview purposes.
    """
    target_user_id = user_id or user.id
    try:
        stats = StatsDbService(db).get_stats(user_id=target_user_id)
        return [StatOut.model_validate(stat) for stat in stats]
    except CornerPocketError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats/summary/all", response_model=list[StatOut])
def summary_all(
    user_id: int | None = Query(None, description="Optional user ID to filter stats"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[StatOut]:
    """Return a simple summary of results for all users.

    Defaults to the current user. Another user's id may be supplied by query
    for administrative/preview purposes.
    """
    try:
        if user_id is not None:
            stats = StatsDbService(db).get_stats(user_id=user_id)
        else:
            stats = StatsDbService(db).get_stats_all()
        return [StatOut.model_validate(stat) for stat in stats]
    except CornerPocketError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats/summary/all/{game_type}", response_model=list[StatOut])
def summary_all_by_game_type(
    game_type: GameType,
    user_id: int | None = Query(None, description="Optional user ID to filter stats"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[StatOut]:
    """Return a simple summary of results for all users by game type.

    Defaults to the current user. Another user's id may be supplied by query
    for administrative/preview purposes.
    """
    try:
        stats = StatsDbService(db).get_stats_by_game_type(game_type=game_type, user_id=user_id)
        return [StatOut.model_validate(stat) for stat in stats]
    except CornerPocketError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats/summary/{game_type}", response_model=list[StatOut])
def summary_by_game_type(
    game_type: GameType,
    user_id: int | None = Query(None, description="The user ID to fetch stats for"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[StatOut]:
    """Return a simple summary of results for a user by game type.

    Defaults to the current user. Another user's id may be supplied by query
    for administrative/preview purposes.
    """
    target_user_id = user_id or user.id

    try:
        stats = StatsDbService(db).get_stats_by_game_type(
            game_type=game_type, user_id=target_user_id
        )
        return [StatOut.model_validate(stat) for stat in stats]
    except CornerPocketError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))