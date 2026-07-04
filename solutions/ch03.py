"""Chapter 3 reference solution."""

from decimal import Decimal

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
    # rowcount is unreliable for executemany (-1 on many drivers); counting
    # RETURNING rows is exact, and 2.0's insertmanyvalues keeps it one statement.
    with engine.begin() as conn:
        result = conn.execute(insert(books).returning(books.c.id), rows)
        return len(result.all())


def titles_in_genre(engine: Engine, genre: str) -> list[str]:
    stmt = select(books.c.title).where(books.c.genre == genre).order_by(books.c.title)
    with engine.connect() as conn:
        return list(conn.execute(stmt).scalars().all())


def average_price_by_genre(engine: Engine) -> dict[str, float]:
    stmt = select(
        books.c.genre,
        func.round(func.avg(books.c.price), 2).label("avg_price"),
    ).group_by(books.c.genre)
    with engine.connect() as conn:
        return {genre: float(avg) for genre, avg in conn.execute(stmt)}


def apply_discount(engine: Engine, genre: str, percent: int) -> list[tuple[str, float]]:
    # Decimal, not float: price is NUMERIC, and Postgres has no
    # round(double precision, int) — numeric * float would produce one.
    factor = Decimal(100 - percent) / 100
    stmt = (
        update(books)
        .where(books.c.genre == genre)
        .values(price=func.round(books.c.price * factor, 2))
        .returning(books.c.title, books.c.price)
    )
    with engine.begin() as conn:
        return [(title, float(price)) for title, price in conn.execute(stmt)]
