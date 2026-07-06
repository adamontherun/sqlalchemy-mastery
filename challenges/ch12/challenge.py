"""Chapter 12 challenge — wire SQLAlchemy into FastAPI yourself.

Make `uv run pytest challenges/ch12` pass.

You get the models and the route signatures; you write the integration:
the session factory, the session-per-request dependency, and the endpoint
bodies. The tests call your app through httpx against the real database —
including a request that fails mid-transaction and must roll back cleanly.
"""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy import ForeignKey, String, func, select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    selectinload,
)


class Base(DeclarativeBase):
    pass


class Board(Base):
    __tablename__ = "ch12_boards"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    cards: Mapped[list["Card"]] = relationship(back_populates="board", cascade="all, delete-orphan")


class Card(Base):
    __tablename__ = "ch12_cards"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    board_id: Mapped[int] = mapped_column(ForeignKey("ch12_boards.id"))
    board: Mapped[Board] = relationship(back_populates="cards")


class CardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str


class BoardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    cards: list[CardOut]


def build_app(engine: AsyncEngine) -> FastAPI:
    """Assemble and return the FastAPI app, given a ready engine.

    You must:
      1. Create ONE async_sessionmaker here (remember ch08's mandatory kwarg).
      2. Implement get_session as a dependency: yield a session, commit on
         success, roll back if the endpoint raised.
      3. Implement the three endpoints:

         POST /boards            body {"name": ...}
            -> 201, BoardOut. Duplicate name -> let the rollback happen and
               return 409 (catch IntegrityError).

         POST /boards/{board_id}/cards   body {"title": ...}
            -> 201, CardOut. Unknown board -> 404.

         GET /boards
            -> 200, list[BoardOut] ordered by name — cards included, which
               means eager loading. Response serialization may touch the
               relationship after your path function returns, so don't leave it
               to async lazy loading.
    """
    app = FastAPI()

    # ... your session factory + dependency here ...

    # ... your endpoints here ...

    raise NotImplementedError("assemble the app")
