import pytest

from corner_pocket_backend.services.users import UsersDbService
from corner_pocket_backend.models import User


class TestUsersDbService:
    def test_create_and_get_user(self, db_session):
        svc = UsersDbService(db=db_session)
        created = svc.create(
            email="alpha@test.com",
            handle="alpha",
            display_name="Alpha",
            password_hash="not_ashash_lolz",
        )
        assert isinstance(created, User)
        assert created.id is not None
        assert created.email == "alpha@test.com"
        assert created.handle == "alpha"
        assert created.display_name == "Alpha"
        assert created.password_hash == "not_ashash_lolz"

        fetched = svc.get_by_email("alpha@test.com")
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.email == "alpha@test.com"
        assert fetched.handle == "alpha"
        assert fetched.display_name == "Alpha"
        assert fetched.password_hash == "not_ashash_lolz"

    def test_unique_email_and_handle(self, db_session):
        svc = UsersDbService(db=db_session)
        svc.create(
            email="dup@test.com",
            handle="dup1",
            display_name="Dup 1",
            password_hash="not_ashash_lolz",
        )
        db_session.commit()  # SQLite needs commit to enforce unique constraints

        # Duplicate email should fail
        with pytest.raises(Exception):
            svc.create(
                email="dup@test.com",
                handle="dup2",
                display_name="Dup 2",
                password_hash="not_ashash_lolz",
            )

        # Duplicate handle should fail
        with pytest.raises(Exception):
            svc.create(
                email="other@test.com",
                handle="dup1",
                display_name="Other",
                password_hash="not_ashash_lolz",
            )
