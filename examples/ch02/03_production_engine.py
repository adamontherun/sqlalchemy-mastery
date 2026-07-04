"""A production-shaped engine, with the pool's lifecycle made visible.

Run me:  uv run examples/ch02/03_production_engine.py
"""

from sqlalchemy import create_engine, event, text

engine = create_engine(
    "postgresql+psycopg://course:course@localhost:5439/course",
    pool_size=5,           # steady-state connections kept open
    max_overflow=10,       # burst headroom (closed again when idle)
    pool_timeout=30,       # how long a checkout waits before TimeoutError
    pool_pre_ping=True,    # test each connection on checkout ("SELECT 1")
    pool_recycle=1800,     # retire connections older than 30 min
    echo_pool=True,        # log the pool's decisions (demo; off in prod)
)


@event.listens_for(engine, "connect")
def on_connect(dbapi_connection, connection_record):
    # Fires only for NEW database connections — not for pool reuse.
    print(">> pool opened a brand-new DB connection")


@event.listens_for(engine, "checkout")
def on_checkout(dbapi_connection, connection_record, connection_proxy):
    # Fires on EVERY checkout, reused or fresh.
    print(">> connection checked out of the pool")


print("--- first use: pool must create a connection ---")
with engine.connect() as conn:
    conn.execute(text("SELECT 1"))

print("\n--- second use: same connection, reused from the pool ---")
with engine.connect() as conn:
    conn.execute(text("SELECT 1"))

print("\n--- invalidate: simulate a dead connection ---")
with engine.connect() as conn:
    conn.invalidate()  # what pre_ping does for you when the ping fails

print("\n--- next use: pool replaces the invalidated connection ---")
with engine.connect() as conn:
    conn.execute(text("SELECT 1"))

engine.dispose()
