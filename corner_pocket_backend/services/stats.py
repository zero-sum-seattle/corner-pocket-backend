from collections import Counter
from .matches import MATCHES, GAMES

class StatsService:
    """Aggregate basic statistics for users from in-memory match data."""

    def summary(self, user_id: str):
        """Compute a naive score differential by game type for a user.

        Counts wins and losses across approved matches and returns a per-game
        type score differential (wins minus losses). Intended as a placeholder
        until real analytics are implemented.
        """
        by_type = Counter()
        for m in MATCHES.values():
            if m["status"] != "APPROVED":
                continue
            # BUG: This counts games from ALL matches, even ones the user didn't play in.
            # Should filter to matches where user_id is creator or opponent first.
            # Also, losses should only count games where opponent won, not "anyone != user".
            # Will fix when we replace this with proper DB queries.
            wins = sum(1 for g in GAMES.get(m["id"], []) if g.get("winner_user_id") == user_id)
            losses = sum(1 for g in GAMES.get(m["id"], []) if g.get("winner_user_id") != user_id)
            t = m["game_type"]
            by_type[t] += wins - losses
        return {"user_id": user_id, "by_game_type_score_diff": dict(by_type)}
