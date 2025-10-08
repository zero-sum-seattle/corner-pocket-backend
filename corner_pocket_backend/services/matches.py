from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from corner_pocket_backend.models import Match, Game, User, MatchStatus, GameType
from corner_pocket_backend.services.games import GamesDbService


class MatchesDbService:
    """Database-backed Matches service (read-only scaffolding).

    This initial version implements list and get operations against the
    SQLAlchemy models. Create/submit/approve flows can be added incrementally.
    """

    def __init__(self, db: Session):
        """Initialize the service with a database session."""
        self.db = db
        self.game_svc = GamesDbService(db=db)

    def list_matches(
        self,
        creator_id: Optional[int] = None,
        opponent_id: Optional[int] = None,
        status: Optional[str] = None,
        game_type: Optional[GameType] = None,
    ) -> List[Dict[str, Any]]:
        """List matches. If `mine` is True, restrict to matches involving creator_id or opponent_id.

        Args:
            db: SQLAlchemy session.
            creator_id: Current creator user id when filtering by participation.
            opponent_id: Current user id when filtering by participation.
            game_type: Optional game type filter.
            status: Optional status filter.
        """
        q = self.db.query(Match)
        if creator_id is not None and opponent_id is not None:
            if game_type is not None:
                q = q.filter((Match.creator_id == creator_id) & (Match.opponent_id == opponent_id) & (Match.game_type == game_type))
            else:
                q = q.filter((Match.creator_id == creator_id) | (Match.opponent_id == opponent_id))
        if game_type is not None:
            q = q.filter(Match.game_type == game_type)
        if status:
            # Validate status against enum if provided
            try:
                enum_status = MatchStatus(status)
            except Exception:
                enum_status = None
            if enum_status is not None:
                q = q.filter(Match.status == enum_status)

        matches: List[Match] = q.order_by(Match.id.desc()).all()
        return [self._serialize_match(m) for m in matches]

    def get_match(self, user_id: int, match_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single match with related games if the user participates."""
        m = self.db.query(Match).filter(Match.id == match_id).first()
        if not m:
            return None
        if user_id not in (m.creator_id, m.opponent_id):
            return None
        
        result = self._serialize_match(m)
        # attach games
        games: List[Game] = (
            self.db.query(Game)
            .filter(Game.match_id == m.id)
            .order_by(Game.id.asc())
            .all()
        )
        result["games"] = [
            {
                "id": g.id,
                "match_id": g.match_id,
                "game_type": g.game_type.value,
                "winner_user_id": g.winner_user_id,
                "loser_user_id": g.loser_user_id,
                "created_at": g.created_at.isoformat() if g.created_at else None,
            }
            for g in games
        ]
        return result

    def add_match(self, user_id: int, opponent_id: int, game_type: GameType, race_to: int) -> Match:
        """Add a new match to the database."""
        new_m = Match(creator_id=user_id, opponent_id=opponent_id, game_type=game_type, race_to=race_to, status=MatchStatus.PENDING)
        self.db.add(new_m)
        self.db.flush()
        return new_m

    def delete_match(self, user_id: int, match_id: int) -> Match:
        """Delete a match from the database.
        
        Raises:
            ValueError: If match not found.
            PermissionError: If user is not a participant.
        """
        m = self.db.query(Match).filter(Match.id == match_id).first()
        if not m:
            raise ValueError("match not found")
        if user_id not in (m.creator_id, m.opponent_id):
            raise PermissionError("not a participant")
        self.db.delete(m)
        self.db.flush()
        return m
    
    def add_game(
        self, 
        match_id: int, 
        winner_user_id: int, 
        loser_user_id: int, 
        game_type: GameType, 
        acting_user_id: int
    ) -> Game:
        """Append a game result to a pending match.
        
        Raises:
            ValueError: If match not found, not PENDING, or invalid game data.
            PermissionError: If acting user is not a participant.
        """
        m = self.db.get(Match, match_id)
        if not m:
            raise ValueError("match not found")
        if acting_user_id not in (m.creator_id, m.opponent_id):
            raise PermissionError("not a participant")
        if m.status != MatchStatus.PENDING:
            raise ValueError("cannot add games unless match is PENDING")
        
        # Validate that winner and loser are match participants
        if {winner_user_id, loser_user_id} != {m.creator_id, m.opponent_id}:
            raise ValueError("winner and loser must be match participants")
        
        return self.game_svc.add_game(
            match_id=m.id,
            winner_user_id=winner_user_id,
            loser_user_id=loser_user_id,
            game_type=game_type,
        )
    

    def add_games(self, user_id: int, match_id: int, games: List[Game]):
        """Append a list of game results to a pending match."""
        gs = []
        for game in games:
            gs.append(
                self.add_game(match_id=match_id, winner_user_id=game.winner_user_id, loser_user_id=game.loser_user_id, game_type=game.game_type, acting_user_id=user_id)
            )
        
        return gs
    
    def delete_game(self, match_id: int, acting_user_id: int, game_id: int) -> None:
        """Delete a game from the database.
        
        Raises:
            ValueError: If match or game not found.
            PermissionError: If user is not a participant in the match.
        """
        m = self._query_match(match_id)
        
        if acting_user_id not in (m.creator_id, m.opponent_id):
            raise PermissionError("not a participant")
        
        g = self.db.query(Game).filter(Game.id == game_id).first()
        if not g:
            raise ValueError("game not found")
        if g.match_id != match_id:
            raise ValueError("game does not belong to this match")
        
        self.game_svc.delete_game(game_id=game_id)
    
    def delete_games(self, match_id: int, acting_user_id: int, game_ids: List[int]) -> None:
        """Delete a list of games from the database."""
        for game_id in game_ids:
            self.delete_game(match_id=match_id, acting_user_id=acting_user_id, game_id=game_id)
    
    def edit_game(
        self, 
        match_id: int, 
        acting_user_id: int, 
        game_id: int, 
        winner_user_id: int, 
        loser_user_id: int
    ) -> Game:
        """Edit a game in the database.
        
        Raises:
            ValueError: If match or game not found.
            PermissionError: If user is not a participant in the match.
        """
        m = self._query_match(match_id)
        
        if acting_user_id not in (m.creator_id, m.opponent_id):
            raise PermissionError("not a participant")
        
        g = self.db.query(Game).filter(Game.id == game_id).first()
        if not g:
            raise ValueError("game not found")
        if g.match_id != match_id:
            raise ValueError("game does not belong to this match")
        
        # Validate that winner and loser are different
        if winner_user_id == loser_user_id:
            raise ValueError("winner and loser must be different")

        # Validate that winner and loser are match participants
        if {winner_user_id, loser_user_id} != {m.creator_id, m.opponent_id}:
            raise ValueError("winner and loser must be match participants")
        
        return self.game_svc.edit_game(
            game_id=game_id, 
            winner_user_id=winner_user_id, 
            loser_user_id=loser_user_id
        )
    
    def edit_match(self, user_id: int, match_id: int, status: MatchStatus) -> Match:
        """Edit a match (e.g., update status)."""
        m = self._query_match(match_id)
        if user_id not in (m.creator_id, m.opponent_id):
            raise PermissionError("not a participant")
        m.status = status
        self.db.flush()
        return m

    def _serialize_match(self, m: Match) -> Dict[str, Any]:
        return {
            "id": m.id,
            "creator_id": m.creator_id,
            "opponent_id": m.opponent_id,
            "game_type": m.game_type.value if hasattr(m.game_type, "value") else str(m.game_type),
            "race_to": m.race_to,
            "status": m.status.value if hasattr(m.status, "value") else str(m.status),
        }

    def _query_match(self, match_id: int) -> Match:
        """Helper to fetch and validate match existence.
        
        Raises:
            ValueError: If match not found.
        """
        m = self.db.query(Match).filter(Match.id == match_id).first()
        if not m:
            raise ValueError("match not found")
        return m
 
