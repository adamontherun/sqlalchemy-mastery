"""The N+1 problem, measured — then fixed three ways.

Run me:  uv run examples/ch07/03_n_plus_one.py
"""

from sqlalchemy import ForeignKey, String, create_engine, event, select
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, Session, joinedload, mapped_column,
    raiseload, relationship, selectinload,
)


class Base(DeclarativeBase):
    pass


class Band(Base):
    __tablename__ = "ch07_bands"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    albums: Mapped[list["Album"]] = relationship(back_populates="band")


class Album(Base):
    __tablename__ = "ch07_albums"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    band_id: Mapped[int] = mapped_column(ForeignKey("ch07_bands.id"))
    band: Mapped[Band] = relationship(back_populates="albums")


engine = create_engine("postgresql+psycopg://course:course@localhost:5439/course")
Base.metadata.create_all(engine)

query_count = 0


@event.listens_for(engine, "before_cursor_execute")
def count_queries(conn, cursor, statement, parameters, context, executemany):
    global query_count
    query_count += 1


with Session(engine) as session:
    for i in range(10):
        band = Band(name=f"Band {i:02d}")
        band.albums = [Album(title=f"Album {i:02d}-{j}") for j in range(3)]
        session.add(band)
    session.commit()

# ---- the accident --------------------------------------------------------
with Session(engine) as session:
    query_count = 0
    bands = session.scalars(select(Band)).all()          # 1 query
    total = sum(len(band.albums) for band in bands)      # +1 query PER BAND
    print(f"lazy loading:      {total} albums fetched with {query_count} queries  <- N+1!")

# ---- fix 1: selectinload — the default answer for collections ------------
with Session(engine) as session:
    query_count = 0
    bands = session.scalars(select(Band).options(selectinload(Band.albums))).all()
    total = sum(len(band.albums) for band in bands)
    print(f"selectinload:      {total} albums fetched with {query_count} queries")

# ---- fix 2: joinedload — best for many-to-one ----------------------------
with Session(engine) as session:
    query_count = 0
    albums = session.scalars(
        select(Album).options(joinedload(Album.band))    # LEFT OUTER JOIN
    ).all()
    names = {album.band.name for album in albums}
    print(f"joinedload:        {len(albums)} albums + their {len(names)} bands in {query_count} query")

# ---- fix 3: raiseload — make hidden IO a loud error ----------------------
with Session(engine) as session:
    bands = session.scalars(select(Band).options(raiseload(Band.albums))).all()
    try:
        _ = bands[0].albums
    except Exception as exc:
        print(f"raiseload:         {type(exc).__name__}: {exc}")

Base.metadata.drop_all(engine)
engine.dispose()
