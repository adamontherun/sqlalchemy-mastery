"""Chapter 5 reference solution."""

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
    with session_factory() as session:
        player = Player(handle=handle)
        session.add(player)
        session.flush()  # INSERT runs; player.id is populated
        player_id = player.id  # read before commit expires attributes
        session.commit()
        return player_id


def rename_player(session_factory: sessionmaker, player_id: int, new_handle: str) -> None:
    with session_factory() as session:
        player = session.get(Player, player_id)
        player.handle = new_handle  # the unit of work notices; UPDATE at commit
        session.commit()


def add_score(session_factory: sessionmaker, handle: str, points: int) -> int:
    with session_factory() as session:
        player = session.scalars(select(Player).where(Player.handle == handle)).one()
        player.score += points
        session.flush()
        new_total = player.score
        session.commit()
        return new_total


def top_players(session_factory: sessionmaker, n: int) -> list[tuple[str, int]]:
    stmt = select(Player.handle, Player.score).order_by(Player.score.desc(), Player.handle).limit(n)
    with session_factory() as session:
        return [tuple(row) for row in session.execute(stmt)]
