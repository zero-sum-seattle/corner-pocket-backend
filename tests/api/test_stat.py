from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from corner_pocket_backend.services.stats import StatsDbService
from corner_pocket_backend.models.users import User
from corner_pocket_backend.models.games import GameType
from corner_pocket_backend.schemas.stats import StatOut


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
        assert response.json() == [StatOut.model_validate(stat).model_dump()]
        print(response.json())
        print([StatOut.model_validate(stat).model_dump(mode="json")])
        assert len(response.json()) == 1
        assert response.json()[0]["user_id"] == create_user.id
        assert response.json()[0]["game_type"] == GameType.EIGHT_BALL
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
        stat2 = svc.create_stat(user_id=create_user.id, game_type=GameType.NINE_BALL) # noqa: F841

        response = client.get(
            f"/api/v1/stats/summary/{GameType.EIGHT_BALL.value}",
            params={"user_id": create_user.id},
            headers={"Authorization": f"Bearer {login_user}"},
        )
        assert response.status_code == 200
        assert response.json() == [StatOut.model_validate(stat1).model_dump(mode="json")]
        assert len(response.json()) == 1
        assert response.json()[0]["user_id"] == create_user.id
        assert response.json()[0]["game_type"] == GameType.EIGHT_BALL
        assert response.json()[0]["period_start"] is None
        assert response.json()[0]["period_end"] is None
        assert response.json()[0]["matches_played"] == 0
