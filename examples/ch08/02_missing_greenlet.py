"""MissingGreenlet: meet async SQLAlchemy's most famous exception — on purpose.

Run me:  uv run examples/ch08/02_missing_greenlet.py
"""

import asyncio

from sqlalchemy import ForeignKey, String, select
from sqlalchemy.exc import MissingGreenlet
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    selectinload,
)


class Base(AsyncAttrs, DeclarativeBase):  # AsyncAttrs => .awaitable_attrs
    pass


class Author(Base):
    __tablename__ = "ch08_authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    books: Mapped[list["Book"]] = relationship(back_populates="author")


class Book(Base):
    __tablename__ = "ch08_books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author_id: Mapped[int] = mapped_column(ForeignKey("ch08_authors.id"))
    author: Mapped[Author] = relationship(back_populates="books")


async def main() -> None:
    engine = create_async_engine("postgresql+asyncpg://course:course@localhost:5439/course")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as session:
        session.add(
            Author(
                name="Ursula K. Le Guin",
                books=[
                    Book(title="The Left Hand of Darkness"),
                    Book(title="The Dispossessed"),
                ],
            )
        )
        await session.commit()

    # ---- trap 1: lazy loading -------------------------------------------
    async with factory() as session:
        author = (await session.scalars(select(Author))).one()
        try:
            _ = author.books  # plain attribute access = hidden IO = boom
        except MissingGreenlet as exc:
            print("lazy load    ->", type(exc).__name__, "(as promised)")

        # fix A: ask explicitly, awaiting the IO
        books = await author.awaitable_attrs.books
        print("AsyncAttrs   ->", [b.title for b in books])

    # fix B (usually best): don't be lazy in the first place
    async with factory() as session:
        author = (await session.scalars(select(Author).options(selectinload(Author.books)))).one()
        print("selectinload ->", [b.title for b in author.books], "(no await needed)")

    # ---- trap 2: expire_on_commit ---------------------------------------
    strict_factory = async_sessionmaker(engine)  # default expire_on_commit=True
    async with strict_factory() as session:
        author = (await session.scalars(select(Author))).one()
        await session.commit()  # every attribute now expired...
        try:
            _ = author.name  # ...so even a plain column is hidden IO
        except MissingGreenlet as exc:
            print(
                "post-commit  ->",
                type(exc).__name__,
                "(this is why async_sessionmaker(expire_on_commit=False))",
            )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


asyncio.run(main())
