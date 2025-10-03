from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from corner_pocket_backend.models import Match, Game, User, MatchStatus, GameType



class GamesDbService:
    """Service for managing games."""

    def __init__(self, db: Session):
        """Initialize the service with a match."""
        self.db = db

    def add_game(self, match_id: str, winner_user_id:str, loser_user_id:str, game_type: GameType) -> Game | None:
        """Add a new game to the database."""
        m = self.db.get(Match, match_id)
        if m is None:
            raise ValueError("match not found")
        game = Game(match_id=match_id, winner_user_id=winner_user_id, loser_user_id=loser_user_id, game_type=game_type)
        if game is None:
            raise ValueError("Game cannot be None")
        m.games.append(game)
        self.db.commit()
        return game

    def delete_game(self, game_id: str) -> Game | None:
        """Delete a game from the database."""
        g = self.db.get(Game, game_id)
        if g is None:
            return None
        self.db.delete(g)
        self.db.commit()
        return g   

    def edit_game(self, game_id: str, winner_user_id:str, loser_user_id:str) -> Game | None:
        """Edit a game in the database."""
        g = self.db.get(Game, game_id)
        if g is None:
            return None
        g.winner_user_id = winner_user_id
        g.loser_user_id = loser_user_id
        self.db.refresh(g)
        self.db.commit()
        return g

    def get_game_type(self, game_id: str) -> GameType | None:
        """Get the type of a game."""
        g = self.db.get(Game, game_id)
        if g is None:
            return None
        return g.game_type