import pytest
from sqlalchemy import String, create_engine, func, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from conftest import DB_URL


class Base(DeclarativeBase):
    pass


class Note(Base):
    __tablename__ = "ch10_notes"
    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str] = mapped_column(String(200))


@pytest.fixture(scope="module")
def engine():
    engine = create_engine(DB_URL)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_start_returns_usable_session(subject, engine):
    harness = subject.TransactionalTestHarness(engine)
    session = harness.start()
    try:
        assert isinstance(session, Session)
        session.add(Note(body="hello"))
        session.commit()
        assert session.scalar(select(func.count(Note.id))) == 1
    finally:
        harness.stop()


def test_commits_are_invisible_after_stop(subject, engine):
    harness = subject.TransactionalTestHarness(engine)
    session = harness.start()
    session.add_all([Note(body="one"), Note(body="two")])
    session.commit()          # a real commit from the test's point of view
    harness.stop()

    with engine.connect() as conn:  # a completely fresh connection
        count = conn.execute(text("SELECT count(*) FROM ch10_notes")).scalar_one()
    assert count == 0, "committed rows leaked past stop() — outer rollback missing?"


def test_consecutive_harnesses_are_isolated(subject, engine):
    for round_number in range(3):
        harness = subject.TransactionalTestHarness(engine)
        session = harness.start()
        assert session.scalar(select(func.count(Note.id))) == 0, (
            f"round {round_number} saw leftovers from a previous round"
        )
        session.add(Note(body=f"round {round_number}"))
        session.commit()
        harness.stop()


def test_no_connection_leak(subject):
    # a pool of one: if stop() doesn't return the connection, round 2 hangs
    small_engine = create_engine(DB_URL, pool_size=1, max_overflow=0, pool_timeout=2)
    Base.metadata.create_all(small_engine)
    try:
        for _ in range(3):
            harness = subject.TransactionalTestHarness(small_engine)
            harness.start()
            harness.stop()
    finally:
        Base.metadata.drop_all(small_engine)
        small_engine.dispose()
