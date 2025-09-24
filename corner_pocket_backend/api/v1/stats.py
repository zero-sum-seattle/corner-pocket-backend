from fastapi import APIRouter, Depends, Query
from typing import Optional
from corner_pocket_backend.services.users import UsersService
from corner_pocket_backend.services.stats import StatsService
from corner_pocket_backend.core.security import get_current_user

router = APIRouter()

@router.get("/stats/summary")
def summary(user_id: Optional[str] = Query(None), user=Depends(get_current_user)):
    """Return a simple summary of results for a user.

    Defaults to the current user. Another user's id may be supplied by query
    for administrative/preview purposes.
    """
    target = user_id or user.id
    return StatsService().summary(user_id=target)
