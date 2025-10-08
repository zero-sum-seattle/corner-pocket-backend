import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from corner_pocket_backend.models import Base, User, Approval, ApprovalStatus, Match, GameType


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
def sample_users(db_session):
    """Create sample users for testing."""
    users = [
        User(handle="creator", email="creator@test.com", display_name="Creator"),
        User(handle="opponent", email="opponent@test.com", display_name="Opponent"),
    ]
    db_session.add_all(users)
    db_session.commit()
    return users


def test_approval_status_enum():
    """Test that ApprovalStatus enum has the expected values."""
    assert ApprovalStatus.PENDING == "PENDING"
    assert ApprovalStatus.APPROVED == "APPROVED"
    assert ApprovalStatus.DECLINED == "DECLINED"


def test_approval_relationships(db_session, sample_users):
    """Test that approval relationships work correctly."""
    creator, opponent = sample_users
    match = Match(
        creator_id=creator.id, opponent_id=opponent.id, game_type=GameType.EIGHT_BALL, race_to=5
    )
    db_session.add(match)
    db_session.commit()
    approval = Approval(
        match_id=match.id, approver_user_id=opponent.id, status=ApprovalStatus.PENDING
    )
    db_session.add(approval)
    db_session.commit()
    assert approval.match == match
    assert approval.approver == opponent, "Approver should be the opponent"


def test_approval_status_defaults_to_pending(db_session, sample_users):
    """Approval.status should default to PENDING when not provided."""
    creator, opponent = sample_users
    match = Match(
        creator_id=creator.id, opponent_id=opponent.id, game_type=GameType.EIGHT_BALL, race_to=5
    )
    db_session.add(match)
    db_session.commit()

    approval = Approval(match_id=match.id, approver_user_id=opponent.id)
    db_session.add(approval)
    db_session.commit()

    assert approval.status == ApprovalStatus.PENDING


def test_approval_one_to_one_uniqueness(db_session, sample_users):
    """Only one Approval row is allowed per Match (unique match_id)."""
    creator, opponent = sample_users
    match = Match(
        creator_id=creator.id, opponent_id=opponent.id, game_type=GameType.EIGHT_BALL, race_to=5
    )
    db_session.add(match)
    db_session.commit()

    first = Approval(match_id=match.id, approver_user_id=opponent.id, status=ApprovalStatus.PENDING)
    db_session.add(first)
    db_session.commit()

    second = Approval(
        match_id=match.id, approver_user_id=opponent.id, status=ApprovalStatus.PENDING
    )
    db_session.add(second)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_approval_foreign_key_constraints(db_session):
    """Test that foreign key constraints work."""
    # Try to create approval with non-existent user IDs
    approval = Approval(match_id=999, approver_user_id=888, status=ApprovalStatus.PENDING)
    db_session.add(approval)
    with pytest.raises(Exception):
        db_session.commit()


def test_approval_required_fields(db_session):
    """Test that required fields cannot be None."""
    approval = Approval(status=ApprovalStatus.PENDING)
    db_session.add(approval)
    with pytest.raises(Exception):
        db_session.commit()


def test_approval_unique_constraints(db_session):
    """Test that approval must be unique per match."""
    # Create users first
    u1 = User(email="u1@test.com", handle="u1", display_name="User 1")
    u2 = User(email="u2@test.com", handle="u2", display_name="User 2")
    db_session.add_all([u1, u2])
    db_session.commit()

    # Create match
    match = Match(creator_id=u1.id, opponent_id=u2.id, game_type=GameType.EIGHT_BALL, race_to=5)
    db_session.add(match)
    db_session.commit()

    # Create first approval
    approval = Approval(match_id=match.id, approver_user_id=u2.id, status=ApprovalStatus.PENDING)
    db_session.add(approval)
    db_session.commit()

    # Try to create duplicate - should fail
    approval2 = Approval(match_id=match.id, approver_user_id=u2.id, status=ApprovalStatus.PENDING)
    db_session.add(approval2)
    with pytest.raises(Exception):
        db_session.commit()


def test_approval_note_field(db_session):
    """Test that note field can be set on approval."""
    u1 = User(email="u1@test.com", handle="u1", display_name="User 1")
    u2 = User(email="u2@test.com", handle="u2", display_name="User 2")
    db_session.add_all([u1, u2])
    db_session.commit()

    match = Match(creator_id=u1.id, opponent_id=u2.id, game_type=GameType.EIGHT_BALL, race_to=5)
    db_session.add(match)
    db_session.commit()

    approval = Approval(
        match_id=match.id, approver_user_id=u2.id, status=ApprovalStatus.PENDING, note="Test note"
    )
    db_session.add(approval)
    db_session.commit()
    assert approval.note == "Test note"
    assert isinstance(approval.note, str)
