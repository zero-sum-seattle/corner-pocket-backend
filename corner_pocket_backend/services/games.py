from typing import Optional

from sqlalchemy.orm import Session

from corner_pocket_backend.models import Match, Game, GameType


class GamesDbService:
    """Service for managing games (low-level CRUD).

    This service handles game-level operations. Authorization and
    business logic should be handled by MatchesDbService.
    """

    def __init__(self, db: Session):
        """Initialize the service with a database session."""
        self.db = db

    def add_game(
        self, match_id: int, winner_user_id: int, loser_user_id: int, game_type: GameType
    ) -> Game:
        """Add a new game to the database.

        Raises:
            ValueError: If match not found or winner/loser are the same.
        """
        m = self.db.get(Match, match_id)
        if m is None:
            raise ValueError("match not found")

        if winner_user_id == loser_user_id:
            raise ValueError("winner and loser must be different")

        game = Game(
            match_id=match_id,
            winner_user_id=winner_user_id,
            loser_user_id=loser_user_id,
            game_type=game_type,
        )
        self.db.add(game)
        self.db.flush()
        return game

    def delete_game(self, game_id: int) -> None:
        """Delete a game from the database.

        Raises:
            ValueError: If game not found.
        """
        g = self.db.get(Game, game_id)
        if g is None:
            raise ValueError("game not found")
        self.db.delete(g)
        self.db.flush()

    def edit_game(self, game_id: int, winner_user_id: int, loser_user_id: int) -> Game:
        """Edit a game in the database.

        Raises:
            ValueError: If game not found or winner/loser are the same.
        """
        g = self.db.get(Game, game_id)
        if g is None:
            raise ValueError("game not found")

        if winner_user_id == loser_user_id:
            raise ValueError("winner and loser must be different")

        g.winner_user_id = winner_user_id
        g.loser_user_id = loser_user_id
        self.db.flush()
        return g

    def get_game(self, game_id: int) -> Optional[Game]:
        """Get a game by ID."""
        return self.db.get(Game, game_id)
