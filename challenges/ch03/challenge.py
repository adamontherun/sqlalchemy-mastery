"""Chapter 3 challenge — Core querying on a tiny bookshop.

Make `uv run pytest challenges/ch03` pass.

The table below is created and seeded by the tests; your job is only the
queries. Use Core constructs — insert()/select()/update()/func — not text().
"""

from sqlalchemy import (
    Column,
    Engine,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    func,
    insert,
    select,
    update,
)

metadata = MetaData()

books = Table(
    "ch03_shop_books",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(200), nullable=False),
    Column("genre", String(50), nullable=False),
    Column("price", Numeric(8, 2), nullable=False),
)


def add_books(engine: Engine, rows: list[dict]) -> int:
    """Insert `rows` (list of {"title": ..., "genre": ..., "price": ...})
    with ONE executed statement, inside one transaction.
    Return how many rows were inserted.

    Gotcha you'll hit if you try Result.rowcount: drivers may report -1 for
    batched ("executemany") inserts. Add .returning(books.c.id) and count
    what comes back instead — SQLAlchemy batches it into a single statement.
    """
    raise NotImplementedError


def titles_in_genre(engine: Engine, genre: str) -> list[str]:
    """All titles in `genre`, alphabetically. Return a plain list of strings.
    Hint: conn.execute(...).scalars().all() unwraps one-column rows.
    """
    raise NotImplementedError


def average_price_by_genre(engine: Engine) -> dict[str, float]:
    """Map genre -> average price (as float, rounded to 2 decimals),
    computed BY THE DATABASE (func.avg + group_by), not in Python.
    """
    raise NotImplementedError


def apply_discount(engine: Engine, genre: str, percent: int) -> list[tuple[str, float]]:
    """Discount every book in `genre` by `percent` (e.g. 10 -> 10% off),
    computing the new price in the database, and return
    [(title, new_price_as_float), ...] via UPDATE ... RETURNING —
    one statement, no follow-up SELECT.
    """
    raise NotImplementedError
