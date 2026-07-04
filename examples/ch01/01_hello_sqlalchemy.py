"""Your first round-trip: prove the whole stack works.

Run me:  uv run examples/ch01/01_hello_sqlalchemy.py
"""

from sqlalchemy import create_engine, text

engine = create_engine("postgresql+psycopg://course:course@localhost:5439/course")

with engine.connect() as conn:
    version = conn.execute(text("SELECT version()")).scalar_one()
    answer = conn.execute(
        text("SELECT :a + :b AS answer"), {"a": 40, "b": 2}
    ).scalar_one()

print(f"Connected to: {version}")
print(f"The database says 40 + 2 = {answer}")
print("Everything works. Welcome to the course!")
