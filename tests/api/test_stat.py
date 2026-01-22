from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from corner_pocket_backend.core.exceptions import CornerPocketError
from corner_pocket_backend.core.password import get_password_hash
from corner_pocket_backend.models.games import GameType
from corner_pocket_backend.models.users import User
from corner_pocket_backend.schemas.stats import StatOut
from corner_pocket_backend.services.stats import StatsDbService


def _create_user(
    db_session: Session, username: str = "testuser", password: str = "password123"
) -> User:
    user = User(
        email=f"{username}@example.com",
        handle=username,
        display_name=f"Test User {username}",
        password_hash=get_password_hash(password),
    )
    db_session.add(user)
    db_session.commit()
    return user


class TestStats:
    def test_summary(
        self, client: TestClient, db_session: Session, create_user: User, login_user: str
    ):
        svc = StatsDbService(db=db_session)

        stat = svc.create_stat(user_id=create_user.id, game_type=GameType.EIGHT_BALL)

        response = client.get(
            "/api/v1/stats/summary",
            params={"user_id": create_user.id},
            headers={"Authorization": f"Bearer {login_user}"},
        )
        assert response.status_code == 200
        assert response.json() == [StatOut.model_validate(stat).model_dump(mode="json")]
        assert len(response.json()) == 1
        assert response.json()[0]["user_id"] == create_user.id
        assert response.json()[0]["game_type"] == GameType.EIGHT_BALL.value
        assert response.json()[0]["period_start"] is None
        assert response.json()[0]["period_end"] is None
        assert response.json()[0]["matches_played"] == 0
        assert response.json()[0]["wins"] == 0
        assert response.json()[0]["losses"] == 0
        assert response.json()[0]["racks_won"] == 0
        assert response.json()[0]["racks_lost"] == 0

    def test_summary_by_game_type(
        self, client: TestClient, db_session: Session, create_user: User, login_user: str
    ):
        svc = StatsDbService(db=db_session)

        stat1 = svc.create_stat(user_id=create_user.id, game_type=GameType.EIGHT_BALL)
        stat2 = svc.create_stat(user_id=create_user.id, game_type=GameType.NINE_BALL)  # noqa: F841

        response = client.get(
            f"/api/v1/stats/summary/{GameType.EIGHT_BALL.value}",
            params={"user_id": create_user.id},
            headers={"Authorization": f"Bearer {login_user}"},
        )
        assert response.status_code == 200
        assert response.json() == [StatOut.model_validate(stat1).model_dump(mode="json")]
        assert len(response.json()) == 1
        assert response.json()[0]["user_id"] == create_user.id
        assert response.json()[0]["game_type"] == GameType.EIGHT_BALL.value
        assert response.json()[0]["period_start"] is None
        assert response.json()[0]["period_end"] is None
        assert response.json()[0]["matches_played"] == 0

    def test_summary_all_by_game_type(
        self, client: TestClient, db_session: Session, create_user: User, login_user: str
    ):
        svc = StatsDbService(db=db_session)

        users = [_create_user(db_session, username=f"user{i}") for i in range(0, 3)]
        for user in users:
            svc.create_stat(user_id=user.id, game_type=GameType.EIGHT_BALL)
            svc.create_stat(user_id=user.id, game_type=GameType.NINE_BALL)  # noqa: F841
            svc.create_stat(user_id=user.id, game_type=GameType.TEN_BALL)  # noqa: F841

        response = client.get(
            f"/api/v1/stats/summary/all/{GameType.EIGHT_BALL.value}",
            headers={"Authorization": f"Bearer {login_user}"},
        )
        assert response.status_code == 200
        assert response.json()[0] == StatOut.model_validate(response.json()[0]).model_dump(
            mode="json"
        )
        assert len(response.json()) == 3

    def test_summary_returns_500_on_db_error(
        self, client: TestClient, db_session: Session, create_user: User, login_user: str
    ):
        """Verify CornerPocketError from service returns 500."""
        with patch.object(
            StatsDbService, "get_stats", side_effect=CornerPocketError("DB connection failed")
        ):
            response = client.get(
                "/api/v1/stats/summary",
                params={"user_id": create_user.id},
                headers={"Authorization": f"Bearer {login_user}"},
            )
            assert response.status_code == 500
            assert "DB connection failed" in response.json()["detail"]

    def test_summary_by_game_type_returns_500_on_db_error(
        self, client: TestClient, db_session: Session, create_user: User, login_user: str
    ):
        """Verify CornerPocketError from service returns 500."""
        with patch.object(
            StatsDbService, "get_stats_by_game_type", side_effect=CornerPocketError("Query failed")
        ):
            response = client.get(
                f"/api/v1/stats/summary/{GameType.EIGHT_BALL.value}",
                params={"user_id": create_user.id},
                headers={"Authorization": f"Bearer {login_user}"},
            )
            assert response.status_code == 500
            assert "Query failed" in response.json()["detail"]

    def test_summary_all_returns_500_on_db_error(
        self, client: TestClient, db_session: Session, create_user: User, login_user: str
    ):
        """Verify CornerPocketError from service returns 500."""
        with patch.object(
            StatsDbService, "get_stats_all", side_effect=CornerPocketError("Connection lost")
        ):
            response = client.get(
                "/api/v1/stats/summary/all",
                headers={"Authorization": f"Bearer {login_user}"},
            )
            assert response.status_code == 500
            assert "Connection lost" in response.json()["detail"]
