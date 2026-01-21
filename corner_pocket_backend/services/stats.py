from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, OperationalError, StatementError
from sqlalchemy.orm.exc import FlushError
from corner_pocket_backend.models import Stat
from corner_pocket_backend.models.games import GameType
from corner_pocket_backend.core.exceptions import CornerPocketError


class StatsDbService:
    """Service for reading and writing persisted user stats."""

    def __init__(self, db: Session):
        """Initialize the stats service with a database session.

        Args:
            db: SQLAlchemy database session for executing queries.
        """
        self.db = db

    def get_stat(self, user_id: int, game_type: GameType) -> Stat | None:
        """Fetch a user's stat row for a specific game type.

        Args:
            user_id: The user to fetch stats for.
            game_type: The game type bucket to return.

        Returns:
            The stat row if found, otherwise None.
        """
        try:
            return (
                self.db.query(Stat)
                .filter(Stat.user_id == user_id, Stat.game_type == game_type)
                .first()
            )
        except IntegrityError as e:
            raise CornerPocketError(f"Error fetching stat: {e}") from e
        except OperationalError as e:
            raise CornerPocketError(f"Error fetching stat: {e}") from e

    def get_stats(self, user_id: int) -> List[Stat]:
        """Fetch all stats for a user across game types.

        Args:
            user_id: The user to fetch stats for.

        Returns:
            A list of stats rows for the user.
        """
        try:
            return self.db.query(Stat).filter(Stat.user_id == user_id).all()
        except IntegrityError as e:
            raise CornerPocketError(f"Error fetching stats: {e}") from e
        except OperationalError as e:
            raise CornerPocketError(f"Error fetching stats: {e}") from e

    def get_stats_by_game_type(self, game_type: GameType, user_id: int | None = None) -> List[Stat]:
        """Fetch stats by game type, optionally filtered by user.

        Args:
            game_type: The game type bucket to fetch stats for.
            user_id: Optional user to filter results.

        Returns:
            A list of stats rows by game type.
        """
        try:
            query = self.db.query(Stat).filter(Stat.game_type == game_type)
            if user_id is not None:
                query = query.filter(Stat.user_id == user_id)
            return query.all()
        except IntegrityError as e:
            raise CornerPocketError(f"Error fetching stats by game type: {e}") from e
        except OperationalError as e:
            raise CornerPocketError(f"Error fetching stats by game type: {e}") from e

    def get_stats_all(self) -> List[Stat]:
        """Fetch all stats for all users across game types.

        Returns:
            A list of stats rows for all users.
        """
        try:
            return self.db.query(Stat).all()
        except IntegrityError as e:
            raise CornerPocketError(f"Error fetching all stats: {e}") from e
        except OperationalError as e:
            raise CornerPocketError(f"Error fetching all stats: {e}") from e

    def create_stat(self, user_id: int, game_type: GameType) -> Stat:
        """Create and return a new stat row for a user and game type.

        Args:
            user_id: The user to create stats for.
            game_type: The game type bucket to create.

        Returns:
            The newly created stat row.
        """
        stat = Stat(
            user_id=user_id,
            game_type=game_type,
            matches_played=0,
            wins=0,
            losses=0,
            racks_won=0,
            racks_lost=0,
        )
        try:
            self.db.add(stat)
            self.db.flush()
        except IntegrityError as e:
            raise CornerPocketError(f"Error creating stat: {e}") from e
        except OperationalError as e:
            raise CornerPocketError(f"Error creating stat: {e}") from e
        except FlushError as e:
            raise CornerPocketError(f"Error creating stat: {e}") from e
        except StatementError as e:
            raise CornerPocketError(f"Error creating stat: {e}") from e
        return stat

    def update_stat(self, stat: Stat) -> Stat:
        """Persist changes to an existing stat row.

        Args:
            stat: The stat row to update.

        Returns:
            The updated stat row.
        """
        try:
            self.db.add(stat)
            self.db.flush()
        except IntegrityError as e:
            raise CornerPocketError(f"Error updating stat: {e}") from e
        except OperationalError as e:
            raise CornerPocketError(f"Error updating stat: {e}") from e
        except FlushError as e:
            raise CornerPocketError(f"Error updating stat: {e}") from e
        except StatementError as e:
            raise CornerPocketError(f"Error updating stat: {e}") from e
        return stat
