"""Chapter 5 challenge — session lifecycle done right.

Make `uv run pytest challenges/ch05` pass.

You get a sessionmaker; every function manages its own short-lived session.
The tests check behavior AND hygiene (no leaked connections).
"""

from sqlalchemy import String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class Player(Base):
    __tablename__ = "ch05_players"
    id: Mapped[int] = mapped_column(primary_key=True)
    handle: Mapped[str] = mapped_column(String(50), unique=True)
    score: Mapped[int] = mapped_column(default=0)


def create_player(session_factory: sessionmaker, handle: str) -> int:
    """Create a player and return their generated id.

    The id must be real (from the database) but the object must be committed.
    Hint: after commit the attribute access still works on a *sync* session —
    or flush first and read the id before committing. Either is fine.
    """
    raise NotImplementedError


def rename_player(session_factory: sessionmaker, player_id: int, new_handle: str) -> None:
    """Load the player, change the handle, persist it.

    This is the unit of work in its natural habitat: NO explicit UPDATE
    statement — load, mutate, commit.
    """
    raise NotImplementedError


def add_score(session_factory: sessionmaker, handle: str, points: int) -> int:
    """Add `points` to the player's score and return the NEW total.

    One session, one transaction. Look the player up by handle
    (select + scalars().one()).
    """
    raise NotImplementedError


def top_players(session_factory: sessionmaker, n: int) -> list[tuple[str, int]]:
    """Return [(handle, score), ...] of the top-n players by score, descending,
    ties broken alphabetically by handle.
    """
    raise NotImplementedError
