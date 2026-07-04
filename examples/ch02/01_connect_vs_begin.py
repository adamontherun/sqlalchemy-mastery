"""The rollback surprise: connect() vs begin().

Run me:  uv run examples/ch02/01_connect_vs_begin.py
"""

from sqlalchemy import create_engine, text

engine = create_engine("postgresql+psycopg://course:course@localhost:5439/course")

with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS ch02_notes"))
    conn.execute(text("CREATE TABLE ch02_notes (body text)"))

# --- Pattern 1: engine.connect() without commit ---------------------------
with engine.connect() as conn:
    conn.execute(text("INSERT INTO ch02_notes VALUES ('I will disappear')"))
    # No conn.commit()! The block ends, the connection returns to the pool,
    # and the pool's reset-on-return ROLLS BACK everything uncommitted.

with engine.connect() as conn:
    count = conn.execute(text("SELECT count(*) FROM ch02_notes")).scalar_one()
print(f"After connect() without commit: {count} rows   <- the INSERT vanished!")

# --- Pattern 2: engine.connect() with explicit commit ----------------------
with engine.connect() as conn:
    conn.execute(text("INSERT INTO ch02_notes VALUES ('committed explicitly')"))
    conn.commit()  # "commit as you go"

# --- Pattern 3: engine.begin() — transaction framing built in --------------
with engine.begin() as conn:  # commits on success, rolls back on exception
    conn.execute(text("INSERT INTO ch02_notes VALUES ('begin() commits for me')"))

with engine.connect() as conn:
    count = conn.execute(text("SELECT count(*) FROM ch02_notes")).scalar_one()
print(f"After explicit commit + begin(): {count} rows")

# Clean up so re-runs start fresh
with engine.begin() as conn:
    conn.execute(text("DROP TABLE ch02_notes"))
engine.dispose()
