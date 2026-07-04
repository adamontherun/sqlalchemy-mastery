"""Three ways to insert 5,000 rows — timed.

Run me:  uv run examples/ch11/01_bulk_inserts.py
"""

import time

from sqlalchemy import String, create_engine, insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Reading(Base):
    __tablename__ = "ch11_readings"
    id: Mapped[int] = mapped_column(primary_key=True)
    sensor: Mapped[str] = mapped_column(String(50))
    value: Mapped[int]


N = 5_000
engine = create_engine("postgresql+psycopg://course:course@localhost:5439/course")
Base.metadata.create_all(engine)


def reset() -> None:
    with engine.begin() as conn:
        conn.execute(Reading.__table__.delete())


def timed(label: str, fn) -> None:
    reset()
    start = time.perf_counter()
    fn()
    print(f"  {label:<38} {time.perf_counter() - start:6.2f}s")


def worst_commit_each() -> None:
    # one INSERT + one COMMIT (fsync!) per row — the anti-pattern
    with Session(engine) as session:
        for i in range(N):
            session.add(Reading(sensor=f"s{i % 10}", value=i))
            session.commit()


def better_one_commit() -> None:
    # ORM unit of work batches via insertmanyvalues; one transaction
    with Session(engine) as session:
        session.add_all(
            Reading(sensor=f"s{i % 10}", value=i) for i in range(N)
        )
        session.commit()


def fastest_core_executemany() -> None:
    # no ORM objects at all: dicts straight into an executemany
    with engine.begin() as conn:
        conn.execute(
            insert(Reading),
            [{"sensor": f"s{i % 10}", "value": i} for i in range(N)],
        )


print(f"inserting {N:,} rows, three ways:")
timed("commit per row (never do this)", worst_commit_each)
timed("ORM add_all + one commit", better_one_commit)
timed("Core insert() executemany", fastest_core_executemany)

print("\nLesson 1: transactions, not statements, dominate cost — commit once.")
print("Lesson 2: if rows aren't objects with behavior, skip the ORM layer.")

Base.metadata.drop_all(engine)
engine.dispose()
