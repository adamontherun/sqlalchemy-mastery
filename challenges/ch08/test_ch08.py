import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from conftest import ASYNC_DB_URL


@pytest.fixture()
async def engine(subject):
    engine = create_async_engine(ASYNC_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(subject.Base.metadata.drop_all)
        await conn.run_sync(subject.Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(subject.Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture()
def factory(subject, engine):
    return subject.make_session_factory(engine)


async def test_create_playlist_returns_id(subject, factory):
    pid = await subject.create_playlist(factory, "Focus", ["Weightless", "Avril 14th"])
    assert isinstance(pid, int)


async def test_created_graph_is_committed(subject, factory):
    await subject.create_playlist(factory, "Focus", ["Weightless"])
    # a brand-new session (even a new pool connection) must see it
    assert await subject.song_count(factory) == 1


async def test_playlists_with_songs_survives_session_close(subject, factory):
    await subject.create_playlist(factory, "Focus", ["Weightless", "Avril 14th"])
    await subject.create_playlist(factory, "Hype", ["Killing in the Name"])
    result = await subject.playlists_with_songs(factory)
    assert result == {
        "Focus": ["Weightless", "Avril 14th"],
        "Hype": ["Killing in the Name"],
    }


async def test_song_count(subject, factory):
    assert await subject.song_count(factory) == 0
    await subject.create_playlist(factory, "Hype", ["One", "Two", "Three"])
    assert await subject.song_count(factory) == 3
