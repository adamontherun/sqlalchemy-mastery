"""Chapter 12 reference solution."""

from typing import Annotated, AsyncIterator

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import ForeignKey, String, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    AsyncEngine, AsyncSession, async_sessionmaker,
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship, selectinload,
)


class Base(DeclarativeBase):
    pass


class Board(Base):
    __tablename__ = "ch12_boards"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    cards: Mapped[list["Card"]] = relationship(
        back_populates="board", cascade="all, delete-orphan"
    )


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


class BoardIn(BaseModel):
    name: str


class CardIn(BaseModel):
    title: str


def build_app(engine: AsyncEngine) -> FastAPI:
    app = FastAPI()
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def get_session() -> AsyncIterator[AsyncSession]:
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    SessionDep = Annotated[AsyncSession, Depends(get_session)]

    @app.post("/boards", response_model=BoardOut, status_code=201)
    async def create_board(payload: BoardIn, session: SessionDep) -> Board:
        board = Board(name=payload.name, cards=[])
        session.add(board)
        try:
            await session.flush()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(409, "board name already exists")
        return board

    @app.post("/boards/{board_id}/cards", response_model=CardOut, status_code=201)
    async def create_card(board_id: int, payload: CardIn, session: SessionDep) -> Card:
        board = await session.get(Board, board_id)
        if board is None:
            raise HTTPException(404, "no such board")
        card = Card(title=payload.title, board=board)
        session.add(card)
        await session.flush()
        return card

    @app.get("/boards", response_model=list[BoardOut])
    async def list_boards(session: SessionDep) -> list[Board]:
        result = await session.scalars(
            select(Board).options(selectinload(Board.cards)).order_by(Board.name)
        )
        return list(result)

    return app
