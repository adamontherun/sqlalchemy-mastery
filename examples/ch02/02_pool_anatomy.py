"""Watch the connection pool breathe — and choke.

Run me:  uv run examples/ch02/02_pool_anatomy.py
"""

from sqlalchemy import create_engine, text
from sqlalchemy.exc import TimeoutError as PoolTimeoutError

# A deliberately tiny pool so we can exhaust it in demo time:
# 2 persistent slots + 1 overflow = 3 concurrent checkouts max.
engine = create_engine(
    "postgresql+psycopg://course:course@localhost:5439/course",
    pool_size=2,
    max_overflow=1,
    pool_timeout=1.5,  # give up after 1.5s instead of the default 30s
)

print("Fresh engine:        ", engine.pool.status())

held = [engine.connect() for _ in range(3)]  # check out ALL capacity
print("3 connections held:  ", engine.pool.status())

print("\nAsking for a 4th connection (this is what a leak feels like)...")
try:
    engine.connect()
except PoolTimeoutError as exc:
    print(f"  -> {type(exc).__name__}: {exc}")

print("\nThis exact error in production almost always means connections are")
print("being checked out and never returned — not that you need a bigger pool.")

held[0].close()  # return ONE connection...
print("\nAfter one close():   ", engine.pool.status())

with engine.connect() as conn:  # ...and the 4th request succeeds instantly
    ok = conn.execute(text("SELECT 'no more waiting'")).scalar_one()
print(f"4th checkout now works: {ok!r}")

for conn in held[1:]:
    conn.close()
engine.dispose()
