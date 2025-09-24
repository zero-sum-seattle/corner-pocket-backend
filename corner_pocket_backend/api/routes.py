from fastapi import APIRouter
from .v1 import auth, matches, stats

router = APIRouter()
router.include_router(auth.router, tags=["auth"])  # Authentication & user session endpoints
router.include_router(matches.router, tags=["matches"])  # Match lifecycle APIs
router.include_router(stats.router, tags=["stats"])  # Stats and summaries
