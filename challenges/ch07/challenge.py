"""Chapter 7 challenge — relationships under a query budget.

Make `uv run pytest challenges/ch07` pass.

The tests COUNT YOUR QUERIES with an event listener. Correct answers
produced by N+1 loops will fail — you must use loader options.
"""

from sqlalchemy import ForeignKey, String, select
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, Session, joinedload, mapped_column,
    relationship, selectinload,
)


class Base(DeclarativeBase):
    pass


class Team(Base):
    __tablename__ = "ch07_teams"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    # TODO: relationship to Player, back_populates, delete-orphan cascade
    # players: Mapped[list["Player"]] = ...


class Player(Base):
    __tablename__ = "ch07_players"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    goals: Mapped[int] = mapped_column(default=0)
    team_id: Mapped[int] = mapped_column(ForeignKey("ch07_teams.id"))

    # TODO: relationship back to Team
    # team: Mapped[Team] = ...


def rosters(session: Session) -> dict[str, list[str]]:
    """{team_name: [player names sorted by goals desc], ...} for ALL teams.

    Query budget: at most 2 SELECTs (hint: selectinload; sort the players
    in the query with an order_by ON THE RELATIONSHIP or in Python — both fine).
    """
    raise NotImplementedError


def top_scorer_teams(session: Session, min_goals: int) -> list[tuple[str, str]]:
    """[(player_name, team_name), ...] for players with >= min_goals goals,
    ordered by goals descending.

    Query budget: exactly 1 SELECT (hint: joinedload on the many-to-one —
    or select both entities with an explicit join).
    """
    raise NotImplementedError
