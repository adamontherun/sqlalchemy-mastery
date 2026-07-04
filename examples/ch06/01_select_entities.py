"""select() with entities: scalars, get, and the shapes of results.

Run me:  uv run examples/ch06/01_select_entities.py
"""

from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Film(Base):
    __tablename__ = "ch06_films"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    director: Mapped[str] = mapped_column(String(100))
    year: Mapped[int]

    def __repr__(self) -> str:
        return f"Film({self.title!r}, {self.year})"


engine = create_engine("postgresql+psycopg://course:course@localhost:5439/course")
Base.metadata.create_all(engine)

with Session(engine) as session:
    session.add_all([
        Film(title="Arrival", director="Denis Villeneuve", year=2016),
        Film(title="Dune", director="Denis Villeneuve", year=2021),
        Film(title="Annihilation", director="Alex Garland", year=2018),
        Film(title="Ex Machina", director="Alex Garland", year=2014),
    ])
    session.commit()

    # select(Entity) yields ROWS of one element: (Film,). scalars() unwraps.
    films = session.scalars(
        select(Film).where(Film.year >= 2016).order_by(Film.year)
    ).all()
    print("scalars().all() ->", films)

    # get(): primary-key lookup, identity-map aware (may skip SQL entirely)
    print("get(1) ->", session.get(Film, 1))

    # exactly-one semantics, loudly enforced
    dune = session.scalars(select(Film).where(Film.title == "Dune")).one()
    print("one() ->", dune)

    # column selections come back as named-tuple Rows, like Core
    rows = session.execute(
        select(Film.title, Film.director).order_by(Film.title)
    ).all()
    for title, director in rows:
        print(f"  {title:<14} — {director}")

Base.metadata.drop_all(engine)
engine.dispose()
