"""A complete async FastAPI + SQLAlchemy service in one readable file.

Run me:
    uv run uvicorn bookmarks_api:app --app-dir examples/ch12 --port 8012

Then try it:
    curl -s localhost:8012/bookmarks -X POST -H 'content-type: application/json' \
         -d '{"url": "https://docs.sqlalchemy.org", "title": "The docs", "tags": ["python", "sql"]}'
    curl -s localhost:8012/bookmarks | python3 -m json.tool
    curl -s localhost:8012/stats
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, ForeignKey, String, Table, func, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    selectinload,
)

DATABASE_URL = "postgresql+asyncpg://course:course@localhost:5439/course"


# ---------------------------------------------------------------- models --


class Base(DeclarativeBase):
    pass


bookmark_tags = Table(
    "ch12_bookmark_tags",
    Base.metadata,
    Column("bookmark_id", ForeignKey("ch12_bookmarks.id"), primary_key=True),
    Column("tag_id", ForeignKey("ch12_tags.id"), primary_key=True),
)


class Bookmark(Base):
    __tablename__ = "ch12_bookmarks"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(2000))
    title: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    tags: Mapped[list["Tag"]] = relationship(secondary=bookmark_tags)


class Tag(Base):
    __tablename__ = "ch12_tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)


# --------------------------------------------------------------- schemas --


class TagOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # read from ORM objects
    name: str


class BookmarkIn(BaseModel):
    url: str
    title: str
    tags: list[str] = []


class BookmarkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    url: str
    title: str
    created_at: datetime
    tags: list[TagOut]


# ------------------------------------------------------ engine lifecycle --


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # ONE engine + ONE sessionmaker for the whole app, built at startup.
    engine = create_async_engine(DATABASE_URL, pool_size=10, pool_pre_ping=True)
    app.state.session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # demo; real apps: Alembic
    yield
    await engine.dispose()  # ch08's rule, honored


app = FastAPI(title="Bookmarks", lifespan=lifespan)


# ------------------------------------------------- session-per-request ----


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """One AsyncSession per request: commit on success, rollback on error."""
    factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


SessionDep = Annotated[AsyncSession, Depends(get_session)]


# -------------------------------------------------------------- endpoints --


@app.post("/bookmarks", response_model=BookmarkOut, status_code=201)
async def create_bookmark(payload: BookmarkIn, session: SessionDep) -> Bookmark:
    # upsert-ish tag handling: reuse existing tags by name
    tags: list[Tag] = []
    if payload.tags:
        existing = {
            t.name: t for t in await session.scalars(select(Tag).where(Tag.name.in_(payload.tags)))
        }
        tags = [existing.get(name) or Tag(name=name) for name in payload.tags]

    bookmark = Bookmark(url=payload.url, title=payload.title, tags=tags)
    session.add(bookmark)
    await session.flush()  # get id + server defaults now
    return bookmark  # serialized AFTER commit: expire_on_commit=False


@app.get("/bookmarks", response_model=list[BookmarkOut])
async def list_bookmarks(session: SessionDep) -> list[Bookmark]:
    result = await session.scalars(
        select(Bookmark)
        .options(selectinload(Bookmark.tags))  # response includes tags -> eager
        .order_by(Bookmark.created_at.desc())
    )
    return list(result)


@app.get("/bookmarks/{bookmark_id}", response_model=BookmarkOut)
async def get_bookmark(bookmark_id: int, session: SessionDep) -> Bookmark:
    bookmark = await session.get(Bookmark, bookmark_id, options=[selectinload(Bookmark.tags)])
    if bookmark is None:
        raise HTTPException(404, "no such bookmark")
    return bookmark


@app.delete("/bookmarks/{bookmark_id}", status_code=204)
async def delete_bookmark(bookmark_id: int, session: SessionDep) -> None:
    bookmark = await session.get(Bookmark, bookmark_id)
    if bookmark is None:
        raise HTTPException(404, "no such bookmark")
    await session.delete(bookmark)


@app.get("/stats")
async def stats(session: SessionDep) -> dict:
    bookmarks = await session.scalar(select(func.count(Bookmark.id)))
    tags = await session.scalar(select(func.count(Tag.id)))
    return {"bookmarks": bookmarks, "tags": tags}
