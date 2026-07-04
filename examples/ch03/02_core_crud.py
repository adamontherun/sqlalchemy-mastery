"""The whole CRUD lifecycle in Core: insert, select, update, delete.

Run me:  uv run examples/ch03/02_core_crud.py
"""

from sqlalchemy import (
    Column, Integer, MetaData, Numeric, String, Table, create_engine,
    delete, insert, select, update,
)

metadata = MetaData()
books = Table(
    "ch03_crud_books", metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(200), nullable=False),
    Column("genre", String(50), nullable=False),
    Column("price", Numeric(8, 2), nullable=False),
)

engine = create_engine("postgresql+psycopg://course:course@localhost:5439/course")
metadata.create_all(engine)

with engine.begin() as conn:
    # -- INSERT one row, getting the generated PK back via RETURNING --------
    result = conn.execute(
        insert(books).returning(books.c.id),
        {"title": "The Left Hand of Darkness", "genre": "sf", "price": 18.99},
    )
    print("inserted id:", result.scalar_one())

    # -- INSERT many: pass a list and the driver batches it ("executemany") -
    conn.execute(
        insert(books),
        [
            {"title": "A Wizard of Earthsea", "genre": "fantasy", "price": 15.50},
            {"title": "The Dispossessed", "genre": "sf", "price": 17.25},
            {"title": "Piranesi", "genre": "fantasy", "price": 14.99},
        ],
    )

    # -- SELECT with where / order_by / limit -------------------------------
    stmt = (
        select(books.c.title, books.c.price)
        .where(books.c.genre == "sf")
        .order_by(books.c.price.desc())
        .limit(5)
    )
    print("\nThe statement is an object; its SQL:\n", stmt, "\n")
    for row in conn.execute(stmt):
        print(f"  {row.title:<28} ${row.price}")

    # -- UPDATE with an expression, not a fetched-then-saved value ----------
    conn.execute(
        update(books)
        .where(books.c.genre == "fantasy")
        .values(price=books.c.price * 0.9)  # 10% off, computed IN the database
    )

    # -- DELETE, and count what's left --------------------------------------
    conn.execute(delete(books).where(books.c.price > 18))
    remaining = conn.execute(select(books.c.title, books.c.price)).all()
    print("\nafter discount + purge of pricey books:")
    for row in remaining:
        print(f"  {row.title:<28} ${row.price}")

metadata.drop_all(engine)
engine.dispose()
