"""Aggregates, mixed selections, and ORM-enabled UPDATE/DELETE.

Run me:  uv run examples/ch06/02_aggregates_and_orm.py
"""

from sqlalchemy import String, create_engine, delete, func, select, update
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Track(Base):
    __tablename__ = "ch06_tracks"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    artist: Mapped[str] = mapped_column(String(100))
    plays: Mapped[int] = mapped_column(default=0)


engine = create_engine("postgresql+psycopg://course:course@localhost:5439/course")
Base.metadata.create_all(engine)

with Session(engine) as session:
    session.add_all([
        Track(title="Everything in Its Right Place", artist="Radiohead", plays=901),
        Track(title="Idioteque", artist="Radiohead", plays=755),
        Track(title="Svefn-g-englar", artist="Sigur Rós", plays=402),
        Track(title="Glósóli", artist="Sigur Rós", plays=311),
        Track(title="Untitled #3", artist="Sigur Rós", plays=97),
    ])
    session.commit()

    # aggregates work exactly like Core — model attributes ARE columns
    stmt = (
        select(Track.artist, func.count().label("n"), func.sum(Track.plays).label("total"))
        .group_by(Track.artist)
        .order_by(func.sum(Track.plays).desc())
    )
    print("-- plays per artist --")
    for artist, n, total in session.execute(stmt):
        print(f"  {artist:<12} {n} tracks, {total:>5} plays")

    # mixed selection: a full entity AND a computed column in each row
    ratio = (Track.plays * 100 / select(func.sum(Track.plays)).scalar_subquery())
    stmt = select(Track, ratio.label("pct")).order_by(ratio.desc()).limit(2)
    print("\n-- top tracks with share of all plays --")
    for track, pct in session.execute(stmt):
        print(f"  {track.title:<35} {pct:.1f}%")

    # ORM-enabled bulk UPDATE/DELETE: set-based SQL, but the session also
    # updates any of these objects it currently holds in memory.
    session.execute(
        update(Track).where(Track.artist == "Sigur Rós").values(plays=Track.plays + 1)
    )
    session.execute(delete(Track).where(Track.plays < 100))
    session.commit()

    print(f"\nafter bulk ops: {session.scalar(select(func.count(Track.id)))} tracks remain")

Base.metadata.drop_all(engine)
engine.dispose()
