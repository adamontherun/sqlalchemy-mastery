"""The canonical rollback-per-test fixture set, sync and async.

Run me:  uv run pytest examples/ch10 -v

Every test gets a Session inside an outer transaction that is rolled back
in teardown. Tests may commit() freely — commits become savepoint releases,
and the teardown rollback erases everything. The database is pristine after
every test, with no TRUNCATE and no re-CREATE.
"""

import pytest
import pytest_asyncio
from sqlalchemy import String, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

DB_URL = "postgresql+psycopg://course:course@localhost:5439/course"
ASYNC_DB_URL = "postgresql+asyncpg://course:course@localhost:5439/course"


class Base(DeclarativeBase):
    pass


class Widget(Base):
    __tablename__ = "ch10_widgets"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


# ---------------------------------------------------------------- sync ----


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)  # schema once per test session
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_session(engine):
    connection = engine.connect()
    outer = connection.begin()  # the transaction no test can commit
    session = Session(
        bind=connection,
        join_transaction_mode="create_savepoint",  # commits -> SAVEPOINTs
    )
    yield session
    session.close()
    outer.rollback()  # everything the test did: gone
    connection.close()


# --------------------------------------------------------------- async ----


@pytest_asyncio.fixture()
async def async_db_session():
    # Engine per test: engines must not hop between pytest-asyncio's loops.
    engine = create_async_engine(ASYNC_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    connection = await engine.connect()
    outer = await connection.begin()
    session = AsyncSession(
        bind=connection,
        join_transaction_mode="create_savepoint",
        expire_on_commit=False,
    )
    yield session
    await session.close()
    await outer.rollback()
    await connection.close()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
