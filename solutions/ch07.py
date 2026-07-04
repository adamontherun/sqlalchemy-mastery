"""Chapter 7 reference solution."""

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

    players: Mapped[list["Player"]] = relationship(
        back_populates="team",
        cascade="all, delete-orphan",
        order_by="Player.goals.desc()",
    )


class Player(Base):
    __tablename__ = "ch07_players"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    goals: Mapped[int] = mapped_column(default=0)
    team_id: Mapped[int] = mapped_column(ForeignKey("ch07_teams.id"))

    team: Mapped[Team] = relationship(back_populates="players")


def rosters(session: Session) -> dict[str, list[str]]:
    teams = session.scalars(
        select(Team).options(selectinload(Team.players))
    ).all()
    return {team.name: [p.name for p in team.players] for team in teams}


def top_scorer_teams(session: Session, min_goals: int) -> list[tuple[str, str]]:
    players = session.scalars(
        select(Player)
        .where(Player.goals >= min_goals)
        .order_by(Player.goals.desc())
        .options(joinedload(Player.team))
    ).all()
    return [(p.name, p.team.name) for p in players]
