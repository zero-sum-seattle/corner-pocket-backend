from collections import Counter
from .matches import MATCHES, GAMES

class StatsService:
    def summary(self, user_id: str):
        by_type = Counter()
        for m in MATCHES.values():
            if m["status"] != "APPROVED":
                continue
            # naive: count wins as all games with user as winner
            wins = sum(1 for g in GAMES.get(m["id"], []) if g.get("winner_user_id") == user_id)
            losses = sum(1 for g in GAMES.get(m["id"], []) if g.get("winner_user_id") != user_id)
            t = m["game_type"]
            by_type[t] += wins - losses
        return {"user_id": user_id, "by_game_type_score_diff": dict(by_type)}
