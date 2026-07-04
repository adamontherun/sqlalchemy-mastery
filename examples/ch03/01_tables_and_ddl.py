"""Schema as data: MetaData, Table, and the DDL they emit.

Run me:  uv run examples/ch03/01_tables_and_ddl.py
"""

from sqlalchemy import (
    Column, ForeignKey, Integer, MetaData, Numeric, String, Table, create_engine,
)
from sqlalchemy.schema import CreateTable

metadata = MetaData()

authors = Table(
    "ch03_authors",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(100), nullable=False),
)

books = Table(
    "ch03_books",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(200), nullable=False),
    Column("genre", String(50), nullable=False),
    Column("price", Numeric(8, 2), nullable=False),
    Column("author_id", ForeignKey("ch03_authors.id"), nullable=False),
)

# A Table is data ABOUT your schema — you can compile it to DDL and look:
engine = create_engine("postgresql+psycopg://course:course@localhost:5439/course")
print(CreateTable(books).compile(engine))

# metadata.create_all() emits CREATE TABLE for anything missing (and no
# ALTER — changing existing tables is Alembic's job, chapter 9).
metadata.create_all(engine)
print("Tables created.")

# drop_all is the mirror image — handy for demos, never for production.
metadata.drop_all(engine)
print("Tables dropped again (this was just a demo).")
engine.dispose()
