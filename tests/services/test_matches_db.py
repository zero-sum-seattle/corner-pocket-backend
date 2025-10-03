from corner_pocket_backend.models import User, Match, MatchStatus, Game, GameType
from corner_pocket_backend.services import MatchesDbService


def seed_users(session) -> tuple[User, User]:
    a = User(email="a@test.com", handle="a", display_name="A")
    b = User(email="b@test.com", handle="b", display_name="B")
    session.add_all([a, b])
    session.commit()
    return a, b


def seed_match_with_games(session, creator: User, opponent: User) -> Match:
    m = Match(creator_id=creator.id, opponent_id=opponent.id, status=MatchStatus.PENDING, game_type=GameType.EIGHT_BALL, race_to=5)
    session.add(m)
    session.commit()
    g1 = Game(match_id=m.id, game_type=GameType.EIGHT_BALL, winner_user_id=creator.id, loser_user_id=opponent.id)
    g2 = Game(match_id=m.id, game_type=GameType.NINE_BALL, winner_user_id=opponent.id, loser_user_id=creator.id)
    session.add_all([g1, g2])
    session.commit()
    return m


def test_list_matches_mine_filters_by_participation(db_session):
    """Test that list_matches filters by participation."""
    m_svc = MatchesDbService(db=db_session)
    u1, u2 = seed_users(db_session)
    m = seed_match_with_games(db_session, u1, u2)

    mine = m_svc.list_matches()
    assert len(mine) == 1
    assert mine[0]["id"] == m.id

    all_matches = m_svc.list_matches(creator_id=u1.id, opponent_id=u2.id)
    assert len(all_matches) == 1


def test_get_match_includes_games_and_requires_participation(db_session):
    """Test that get_match includes games and requires participation."""
    m_svc = MatchesDbService(db=db_session)
    u1, u2 = seed_users(db_session)
    m = seed_match_with_games(db_session, u1, u2)

    result = m_svc.get_match(user_id=u1.id, match_id=m.id)
    assert result is not None
    assert result["id"] == m.id
    assert len(result["games"]) == 2

    # Non-participant cannot fetch
    outsider = User(email="c@test.com", handle="c", display_name="C")
    db_session.add(outsider)
    db_session.commit()
    denied = m_svc.get_match(user_id=outsider.id, match_id=m.id)
    assert denied is None


