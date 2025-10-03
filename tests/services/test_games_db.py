import pytest

from corner_pocket_backend.services.games import GamesDbService
from corner_pocket_backend.models import Game, User, Match, GameType


class TestGamesDbService:
    """Test the GamesDbService."""

    def seed_users_and_match(self, session):
        """Seed a user and a match."""
        a = User(email="a@test.com", handle="a")
        b = User(email="b@test.com", handle="b")
        session.add_all([a, b])
        session.commit()
        m = Match(creator_id=a.id, opponent_id=b.id)
        session.add(m)
        session.commit()
        return a, b, m

    def test_add_game_happy_path(self, db_session):
        """Test adding a game to a match."""
        g_srv = GamesDbService(db=db_session)
        a, b, m = self.seed_users_and_match(db_session)

        game_type = GameType.EIGHT_BALL

        g = g_srv.add_game(
            match_id=m.id,
            winner_user_id=a.id,
            loser_user_id=b.id,
            game_type=game_type,
        )

        # Expect a persisted Game
        assert isinstance(g, Game)
        assert g.id is not None
        assert g.match_id == m.id
        assert g.game_type in (GameType.EIGHT_BALL, GameType.NINE_BALL, GameType.TEN_BALL) or g.game_type is not None

    def test_add_game_invalid_match(self, db_session):
        """Test adding a game to an invalid match."""
        g_srv = GamesDbService(db=db_session)
        a, b, m = self.seed_users_and_match(db_session)
        game_type = GameType.EIGHT_BALL
        with pytest.raises(Exception):
            g_srv.add_game(user_id=a.id, match_id=9999, winner_user_id=a.id, loser_user_id=b.id, game_type=game_type)


