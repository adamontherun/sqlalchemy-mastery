"""One-to-many: relationship(), back_populates, and cascades.

Run me:  uv run examples/ch07/01_one_to_many.py
"""

from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, Session, mapped_column, relationship,
)


class Base(DeclarativeBase):
    pass


class Author(Base):
    __tablename__ = "ch07_authors"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    books: Mapped[list["Book"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",  # books die with their author
    )


class Book(Base):
    __tablename__ = "ch07_books"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author_id: Mapped[int] = mapped_column(ForeignKey("ch07_authors.id"))

    author: Mapped[Author] = relationship(back_populates="books")


engine = create_engine("postgresql+psycopg://course:course@localhost:5439/course")
Base.metadata.create_all(engine)

with Session(engine) as session:
    # Build the object graph in Python; the FK column is never touched by hand.
    le_guin = Author(name="Ursula K. Le Guin")
    le_guin.books.append(Book(title="The Left Hand of Darkness"))
    le_guin.books.append(Book(title="The Dispossessed"))

    # back_populates keeps both sides in sync BEFORE any SQL exists:
    lathe = Book(title="The Lathe of Heaven", author=le_guin)
    print(f"set book.author  -> book in le_guin.books? {lathe in le_guin.books}")

    session.add(le_guin)  # ONE add — the save-update cascade brings all 3 books
    session.commit()

    # navigate the other way
    fetched = session.scalars(
        select(Book).where(Book.title == "The Dispossessed")
    ).one()
    print(f"book.author.name -> {fetched.author.name}")

    # delete-orphan: removing a book from the collection deletes its row
    le_guin.books.remove(fetched)
    session.commit()
    titles = session.scalars(select(Book.title).order_by(Book.title)).all()
    print(f"after remove()   -> {titles}  (the row is gone, not just unlinked)")

Base.metadata.drop_all(engine)
engine.dispose()
