"""Concurrency done right: one AsyncSession per task, one engine per app.

Run me:  uv run examples/ch08/03_concurrency.py
"""

import asyncio

from sqlalchemy import String, func, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = "ch08_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    worker: Mapped[str] = mapped_column(String(50))


async def worker(name: str, factory: async_sessionmaker[AsyncSession]) -> None:
    # Each task opens ITS OWN session. Sessions are single-task creatures;
    # sharing one across gather()ed tasks corrupts its internal state.
    async with factory() as session:
        for _ in range(5):
            session.add(Event(worker=name))
            await session.commit()
            await asyncio.sleep(0)  # yield, so tasks truly interleave


async def main() -> None:
    engine = create_async_engine(
        "postgresql+asyncpg://course:course@localhost:5439/course",
        pool_size=5,
        max_overflow=2,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)

    # 8 concurrent workers, 5 pooled connections: the pool queues fairly.
    await asyncio.gather(*(worker(f"w{i}", factory) for i in range(8)))

    async with factory() as session:
        total = await session.scalar(select(func.count(Event.id)))
        per_worker = (
            await session.execute(
                select(Event.worker, func.count()).group_by(Event.worker).order_by(Event.worker)
            )
        ).all()
    print(f"total events: {total}")
    print("per worker:  ", ", ".join(f"{w}={n}" for w, n in per_worker))

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


asyncio.run(main())
