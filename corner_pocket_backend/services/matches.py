# Stub service for early scaffolding. Replace with DB logic later.
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from uuid import uuid4

MATCHES: Dict[str, dict] = {}
GAMES: Dict[str, list] = {}

@dataclass
class Match:
    id: str
    created_by_user_id: str
    opponent_user_id: str
    game_type: str
    race_to: int | None
    status: str

class MatchesService:
    """In-memory match management service used for early scaffolding.

    Replaced by a real database-backed implementation in a future phase.
    """

    def create_match(self, creator_id: str, opponent_id: str, game_type: str, race_to: int | None):
        """Create a new match in pending state and return its record."""
        mid = str(uuid4())
        m = Match(id=mid, created_by_user_id=creator_id, opponent_user_id=opponent_id,
                  game_type=game_type, race_to=race_to, status="PENDING")
        MATCHES[mid] = asdict(m)
        GAMES[mid] = []
        return MATCHES[mid]

    def list_matches(self, user_id: str, mine: bool = True, status: Optional[str] = None):
        """List matches for a user or all matches, optionally filtering by status."""
        out = []
        for m in MATCHES.values():
            if mine and (m["created_by_user_id"] == user_id or m["opponent_user_id"] == user_id):
                if status and m["status"] != status:
                    continue
                out.append(m)
            elif not mine:
                out.append(m)
        return out

    def get_match(self, user_id: str, match_id: str):
        """Return a match with embedded games if the user is a participant."""
        m = MATCHES.get(match_id)
        if not m:
            return None
        if user_id not in (m["created_by_user_id"], m["opponent_user_id"]):
            return None
        m = dict(m)
        m["games"] = GAMES.get(match_id, [])
        return m

    def add_game(self, user_id: str, match_id: str, winner_user_id: str):
        """Append a game result to a pending match."""
        m = MATCHES.get(match_id)
        if not m or m["status"] != "PENDING":
            return {"error": "Invalid state"}
        GAMES[match_id].append({"winner_user_id": winner_user_id})
        return {"ok": True}

    def submit(self, user_id: str, match_id: str):
        """Submit a match for approval (creator only)."""
        m = MATCHES.get(match_id)
        if not m or m["created_by_user_id"] != user_id or m["status"] != "PENDING":
            return {"error": "Invalid state"}
        m["status"] = "SUBMITTED"
        return m

    def approve(self, user_id: str, match_id: str):
        """Approve a submitted match (opponent only)."""
        m = MATCHES.get(match_id)
        if not m or m["opponent_user_id"] != user_id or m["status"] != "SUBMITTED":
            return {"error": "Invalid state"}
        m["status"] = "APPROVED"
        return m

    def decline(self, user_id: str, match_id: str):
        """Decline a submitted match (opponent only)."""
        m = MATCHES.get(match_id)
        if not m or m["opponent_user_id"] != user_id or m["status"] != "SUBMITTED":
            return {"error": "Invalid state"}
        m["status"] = "DECLINED"
        return m
