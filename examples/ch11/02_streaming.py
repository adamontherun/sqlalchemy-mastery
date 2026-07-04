"""Streaming large result sets: yield_per and server-side cursors.

Run me:  uv run examples/ch11/02_streaming.py
"""

import tracemalloc

from sqlalchemy import String, create_engine, insert, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class LogLine(Base):
    __tablename__ = "ch11_loglines"
    id: Mapped[int] = mapped_column(primary_key=True)
    line: Mapped[str] = mapped_column(String(200))


N = 50_000
engine = create_engine("postgresql+psycopg://course:course@localhost:5439/course")
Base.metadata.create_all(engine)

with engine.begin() as conn:
    conn.execute(
        insert(LogLine),
        [{"line": f"2026-07-03 request {i} took {i % 900}ms"} for i in range(N)],
    )


def peak_mb(fn) -> tuple[int, float]:
    tracemalloc.start()
    count = fn()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return count, peak / 1_048_576


def load_everything() -> int:
    with Session(engine) as session:
        rows = session.scalars(select(LogLine)).all()   # every object at once
        return len(rows)


def stream_in_batches() -> int:
    count = 0
    with Session(engine) as session:
        # yield_per: server-side cursor + objects created in batches of 1000
        for _ in session.scalars(select(LogLine).execution_options(yield_per=1000)):
            count += 1
    return count


n1, mem1 = peak_mb(load_everything)
n2, mem2 = peak_mb(stream_in_batches)
print(f".all() on {n1:,} rows:          peak memory {mem1:6.1f} MB")
print(f"yield_per=1000, same rows:    peak memory {mem2:6.1f} MB")
print("\nSame rows, same order — a fraction of the memory. For ETL/export paths,")
print("streaming is the difference between 'runs nightly' and 'OOM-killed nightly'.")

Base.metadata.drop_all(engine)
engine.dispose()
