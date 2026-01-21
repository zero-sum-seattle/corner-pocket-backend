from corner_pocket_backend.models.users import User
from corner_pocket_backend.models.games import GameType
from corner_pocket_backend.services.stats import StatsDbService


def _create_user(db_session, username: str = "statsuser", email: str = "stats@example.com") -> User:
    user = User(
        email=email,
        handle=username,
        display_name=f"Stats User {username}",
        password_hash="not_a_hash_lolz",
    )
    db_session.add(user)
    db_session.commit()
    return user


class TestStatsDbService:
    def test_create_stat_defaults(self, db_session):
        svc = StatsDbService(db=db_session)
        user = _create_user(db_session)

        stat = svc.create_stat(user_id=user.id, game_type=GameType.EIGHT_BALL)

        assert stat.id is not None
        assert stat.user_id == user.id
        assert stat.game_type == GameType.EIGHT_BALL
        assert stat.matches_played == 0
        assert stat.wins == 0
        assert stat.losses == 0
        assert stat.racks_won == 0
        assert stat.racks_lost == 0

    def test_get_stat(self, db_session):
        svc = StatsDbService(db=db_session)
        user = _create_user(db_session)

        created = svc.create_stat(user_id=user.id, game_type=GameType.NINE_BALL)
        fetched = svc.get_stat(user_id=user.id, game_type=GameType.NINE_BALL)

        assert fetched is not None
        assert fetched.id == created.id

    def test_get_stats(self, db_session):
        svc = StatsDbService(db=db_session)
        user = _create_user(db_session)

        svc.create_stat(user_id=user.id, game_type=GameType.EIGHT_BALL)
        svc.create_stat(user_id=user.id, game_type=GameType.NINE_BALL)

        stats = svc.get_stats(user_id=user.id)
        assert len(stats) == 2

    def test_get_stats_by_game_type(self, db_session):
        svc = StatsDbService(db=db_session)
        user1 = _create_user(db_session, username="user1", email="user1@example.com")
        user2 = _create_user(db_session, username="user2", email="user2@example.com")

        svc.create_stat(user_id=user1.id, game_type=GameType.EIGHT_BALL)
        svc.create_stat(user_id=user1.id, game_type=GameType.NINE_BALL)
        svc.create_stat(user_id=user2.id, game_type=GameType.EIGHT_BALL)
        svc.create_stat(user_id=user2.id, game_type=GameType.NINE_BALL)

        stats = svc.get_stats_by_game_type(game_type=GameType.EIGHT_BALL)
        assert len(stats) == 2
        assert stats[0].game_type == GameType.EIGHT_BALL
        assert stats[1].game_type == GameType.EIGHT_BALL

    def test_get_stats_all(self, db_session):
        svc = StatsDbService(db=db_session)
        user = _create_user(db_session)

        svc.create_stat(user_id=user.id, game_type=GameType.EIGHT_BALL)
        svc.create_stat(user_id=user.id, game_type=GameType.NINE_BALL)

        stats = svc.get_stats_all()
        assert len(stats) == 2

    def test_update_stat(self, db_session):
        svc = StatsDbService(db=db_session)
        user = _create_user(db_session)

        stat = svc.create_stat(user_id=user.id, game_type=GameType.EIGHT_BALL)
        stat.wins = 2
        stat.losses = 1
        stat.matches_played = 3

        updated = svc.update_stat(stat)

        assert updated.wins == 2
        assert updated.losses == 1
        assert updated.matches_played == 3
