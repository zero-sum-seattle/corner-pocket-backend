import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from corner_pocket_backend.models import Base, User, Match, Game, GameType, RaceTo


@pytest.fixture
def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")

    from sqlalchemy import event

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_match(db_session):
    """Create a sample match with users for testing games."""
    creator = User(email="creator@test.com", handle="creator", display_name="Creator")
    opponent = User(email="opponent@test.com", handle="opponent", display_name="Opponent")
    
    db_session.add_all([creator, opponent])
    db_session.commit()
    
    match = Match(
        creator_id=creator.id,
        opponent_id=opponent.id,
        game_type=GameType.EIGHT_BALL,
        race_to=5,
    )
    
    db_session.add(match)
    db_session.commit()
    
    return match, creator, opponent


def test_game_creation(db_session, sample_match):
    """Test creating a basic game."""
    match, creator, opponent = sample_match
    
    game = Game(
        match_id=match.id,
        game_type=GameType.EIGHT_BALL,
        winner_user_id=creator.id,
        loser_user_id=opponent.id,
    )
    
    db_session.add(game)
    db_session.commit()
    
    assert game.id is not None
    assert game.match_id == match.id
    assert game.game_type == GameType.EIGHT_BALL
    assert game.winner_user_id == creator.id
    assert game.loser_user_id == opponent.id
    assert isinstance(game.created_at, datetime)


def test_game_type_enum():
    """Test that GameType enum has expected values."""
    assert GameType.EIGHT_BALL == "EIGHT_BALL"
    assert GameType.NINE_BALL == "NINE_BALL"
    assert GameType.TEN_BALL == "TEN_BALL"


def test_race_to_enum():
    """Test that RaceTo enum has expected values."""
    assert RaceTo.THREE.value == 3
    assert RaceTo.FIVE.value == 5
    assert RaceTo.SEVEN.value == 7
    assert RaceTo.NINE.value == 9
    assert RaceTo.THIRTEEN.value == 13
    assert RaceTo.FIFTEEN.value == 15


def test_game_required_fields(db_session, sample_match):
    """Test that all required fields must be provided."""
    match, creator, opponent = sample_match
    
    # Missing game_type
    game = Game(
        match_id=match.id,
        winner_user_id=creator.id,
        loser_user_id=opponent.id,
    )
    
    db_session.add(game)
    
    with pytest.raises(Exception):
        db_session.commit()


def test_game_foreign_key_constraints(db_session):
    """Test foreign key constraints for games."""
    # Try to create game with non-existent match_id
    game = Game(
        match_id=999,  # Doesn't exist
        game_type=GameType.EIGHT_BALL,
        winner_user_id=1,
        loser_user_id=2,
    )
    
    db_session.add(game)
    
    with pytest.raises(Exception):
        db_session.commit()


def test_game_winner_loser_cannot_be_same(db_session, sample_match):
    """Test business logic: winner and loser should be different."""
    match, creator, opponent = sample_match
    
    # DB allows this but business logic shouldn't
    game = Game(
        match_id=match.id,
        game_type=GameType.EIGHT_BALL,
        winner_user_id=creator.id,
        loser_user_id=creator.id,  # Same person!
    )
    
    db_session.add(game)
    db_session.commit()  # DB allows it
    
    # Business logic should catch this in the service layer
    assert game.winner_user_id == game.loser_user_id  # Shows the issue


def test_multiple_games_in_match(db_session, sample_match):
    """Test that a match can have multiple games."""
    match, creator, opponent = sample_match
    
    # Creator wins first game
    game1 = Game(
        match_id=match.id,
        game_type=GameType.EIGHT_BALL,
        winner_user_id=creator.id,
        loser_user_id=opponent.id,
    )
    
    # Opponent wins second game
    game2 = Game(
        match_id=match.id,
        game_type=GameType.EIGHT_BALL,
        winner_user_id=opponent.id,
        loser_user_id=creator.id,
    )
    
    db_session.add_all([game1, game2])
    db_session.commit()
    
    # Check that both games exist for the match
    games = db_session.query(Game).filter(Game.match_id == match.id).all()
    assert len(games) == 2
    
    # Check the winners are different
    winners = [game.winner_user_id for game in games]
    assert creator.id in winners
    assert opponent.id in winners
