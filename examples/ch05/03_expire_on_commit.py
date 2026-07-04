"""expire_on_commit: the default you must understand before Chapter 8.

Run me:  uv run examples/ch05/03_expire_on_commit.py
"""

from sqlalchemy import String, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Cat(Base):
    __tablename__ = "ch05_cats"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


engine = create_engine("postgresql+psycopg://course:course@localhost:5439/course")
Base.metadata.create_all(engine)

statements: list[str] = []


@event.listens_for(engine, "before_cursor_execute")
def count_sql(conn, cursor, statement, parameters, context, executemany):
    statements.append(statement.split()[0])


print("--- default: expire_on_commit=True ---")
with Session(engine) as session:
    cat = Cat(name="Behemoth")
    session.add(cat)
    session.commit()  # every attribute of `cat` is now EXPIRED

    statements.clear()
    print(f"cat.name -> {cat.name!r}")
    print(f"...that attribute access ran SQL: {statements}")
    print("after commit, the session assumes the world changed; first touch reloads\n")

print("--- expire_on_commit=False ---")
with Session(engine, expire_on_commit=False) as session:
    fetched_cat = session.get(Cat, 1)
    assert fetched_cat is not None, "row 1 was just committed above"
    fetched_cat.name = "Behemoth the Great"
    session.commit()

    statements.clear()
    print(f"cat.name -> {fetched_cat.name!r}")
    print(f"...that attribute access ran SQL: {statements or 'none — served from memory'}")

print("\nWhy you care: in async code (ch08) that silent reload-on-touch is not")
print("allowed to do IO and raises MissingGreenlet. In web apps (ch12) it fires")
print("after the session is gone and raises DetachedInstanceError. Same root cause.")

Base.metadata.drop_all(engine)
engine.dispose()
