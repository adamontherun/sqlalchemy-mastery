"""Watching your engine in production: echo, pool status, and slow-query logging.

Run me:  uv run examples/ch11/03_pool_monitoring.py
"""

import time

from sqlalchemy import create_engine, event, text

engine = create_engine(
    "postgresql+psycopg://course:course@localhost:5439/course",
    pool_size=5,
)

# ---- a poor man's slow-query log, two event hooks and a clock -------------
SLOW_MS = 20.0


@event.listens_for(engine, "before_cursor_execute")
def stamp_start(conn, cursor, statement, parameters, context, executemany):
    context._query_start = time.perf_counter()


@event.listens_for(engine, "after_cursor_execute")
def report_slow(conn, cursor, statement, parameters, context, executemany):
    elapsed_ms = (time.perf_counter() - context._query_start) * 1000
    if elapsed_ms > SLOW_MS:
        print(f"  SLOW ({elapsed_ms:6.1f} ms): {statement[:70]}...")


with engine.connect() as conn:
    conn.execute(text("SELECT 1"))  # fast: silent
    conn.execute(text("SELECT pg_sleep(0.05), 1"))  # slow: logged
    print("(only the slow query above got logged)\n")

# ---- pool introspection ----------------------------------------------------
print("pool status:", engine.pool.status())
print("""
In real services, export these as metrics (checked-out count especially) and
alert on sustained checkout == pool_size + max_overflow — that's the leak
signature from chapter 2, visible BEFORE the TimeoutErrors start.

Other production knobs worth knowing:
  * create_engine(echo=True)       — full SQL log (dev only; it's chatty)
  * logging.getLogger("sqlalchemy.engine") — the grown-up version of echo
  * PostgreSQL's pg_stat_activity  — the server's view of your sessions
  * statement caching is automatic in 2.0 — repeated statement shapes show
    a "[cached since ...]" suffix in the echo log; it's why building the
    same select() in a loop is cheaper than it looks.
""")

engine.dispose()
