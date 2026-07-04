"""Chapter 8 reference solution."""

from sqlalchemy import ForeignKey, String, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    selectinload,
)


class Base(DeclarativeBase):
    pass


class Playlist(Base):
    __tablename__ = "ch08_playlists"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    songs: Mapped[list["Song"]] = relationship(
        back_populates="playlist", cascade="all, delete-orphan"
    )


class Song(Base):
    __tablename__ = "ch08_songs"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    playlist_id: Mapped[int] = mapped_column(ForeignKey("ch08_playlists.id"))
    playlist: Mapped[Playlist] = relationship(back_populates="songs")


def make_session_factory(engine) -> async_sessionmaker[AsyncSession]:
    # expire_on_commit=False: post-commit attribute access must not do IO.
    return async_sessionmaker(engine, expire_on_commit=False)


async def create_playlist(
    factory: async_sessionmaker[AsyncSession], name: str, titles: list[str]
) -> int:
    async with factory() as session:
        playlist = Playlist(name=name, songs=[Song(title=t) for t in titles])
        session.add(playlist)
        await session.commit()
        return playlist.id  # safe: expire_on_commit=False


async def playlists_with_songs(
    factory: async_sessionmaker[AsyncSession],
) -> dict[str, list[str]]:
    async with factory() as session:
        playlists = (
            await session.scalars(
                select(Playlist).options(selectinload(Playlist.songs)).order_by(Playlist.id)
            )
        ).all()
        return {p.name: [s.title for s in p.songs] for p in playlists}


async def song_count(factory: async_sessionmaker[AsyncSession]) -> int:
    async with factory() as session:
        return (await session.scalars(select(func.count(Song.id)))).one()
