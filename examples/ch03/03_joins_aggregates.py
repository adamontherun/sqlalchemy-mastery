"""Joins, aggregates, and subqueries — SQL you know, spelled in Python.

Run me:  uv run examples/ch03/03_joins_aggregates.py
"""

from sqlalchemy import (
    Column, ForeignKey, Integer, MetaData, Numeric, String, Table,
    create_engine, func, insert, select,
)

metadata = MetaData()
authors = Table(
    "ch03_ja_authors", metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100)),
)
books = Table(
    "ch03_ja_books", metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(200)),
    Column("price", Numeric(8, 2)),
    Column("author_id", ForeignKey("ch03_ja_authors.id")),
)

engine = create_engine("postgresql+psycopg://course:course@localhost:5439/course")
metadata.create_all(engine)

with engine.begin() as conn:
    conn.execute(insert(authors), [
        {"id": 1, "name": "Ursula K. Le Guin"},
        {"id": 2, "name": "Susanna Clarke"},
    ])
    conn.execute(insert(books), [
        {"title": "The Left Hand of Darkness", "price": 18.99, "author_id": 1},
        {"title": "The Dispossessed", "price": 17.25, "author_id": 1},
        {"title": "Piranesi", "price": 14.99, "author_id": 2},
        {"title": "Jonathan Strange & Mr Norrell", "price": 22.00, "author_id": 2},
    ])

    # JOIN: select_from + join_from make the FROM clause explicit.
    stmt = (
        select(authors.c.name, books.c.title)
        .join_from(authors, books)          # ON inferred from the ForeignKey
        .order_by(authors.c.name, books.c.title)
    )
    print("-- join --")
    for name, title in conn.execute(stmt):
        print(f"  {name:<20} {title}")

    # GROUP BY + aggregate functions live under `func` (func.anything works;
    # it's compiled verbatim, so func.count, func.avg, func.jsonb_agg, ...).
    stmt = (
        select(
            authors.c.name,
            func.count(books.c.id).label("n_books"),
            func.avg(books.c.price).label("avg_price"),
        )
        .join_from(authors, books)
        .group_by(authors.c.name)
        .having(func.count(books.c.id) > 1)
    )
    print("\n-- group by / having --")
    for row in conn.execute(stmt):
        print(f"  {row.name:<20} {row.n_books} books, avg ${row.avg_price:.2f}")

    # Subquery: books priced above the overall average.
    avg_price = select(func.avg(books.c.price)).scalar_subquery()
    stmt = select(books.c.title, books.c.price).where(books.c.price > avg_price)
    print("\n-- above-average books (scalar subquery) --")
    for title, price in conn.execute(stmt):
        print(f"  {title:<32} ${price}")

metadata.drop_all(engine)
engine.dispose()
