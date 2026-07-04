"""Async SQLAlchemy: same API, await in front, asyncpg underneath.

Run me:  uv run examples/ch08/01_async_basics.py
"""

import asyncio

from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Quote(Base):
    __tablename__ = "ch08_quotes"
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(500))
    author: Mapped[str] = mapped_column(String(100))


async def main() -> None:
    # note the driver: +asyncpg, not +psycopg
    engine = create_async_engine("postgresql+asyncpg://course:course@localhost:5439/course")
    print(f"pool class: {type(engine.pool).__name__}")  # AsyncAdaptedQueuePool

    # DDL is sync-only machinery — run_sync bridges it:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # expire_on_commit=False is NOT optional style in async — see 02_...py
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        session.add_all(
            [
                Quote(text="Simple is better than complex.", author="Tim Peters"),
                Quote(
                    text="There are only two hard things in Computer Science: "
                    "cache invalidation and naming things.",
                    author="Phil Karlton",
                ),
            ]
        )
        await session.commit()

    async with session_factory() as session:
        result = await session.scalars(select(Quote).order_by(Quote.id))
        for quote in result:
            print(f'  "{quote.text}" — {quote.author}')

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # ALWAYS dispose an async engine before the event loop dies,
    # or garbage collection greets you with "Event loop is closed".
    await engine.dispose()


asyncio.run(main())
