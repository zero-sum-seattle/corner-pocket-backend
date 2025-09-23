from fastapi import APIRouter
from .v1 import auth, matches, stats

router = APIRouter()
router.include_router(auth.router, tags=["auth"])
router.include_router(matches.router, tags=["matches"])
router.include_router(stats.router, tags=["stats"])
