"""The unit of work: nothing happens until it has to.

Run me:  uv run examples/ch05/01_unit_of_work.py
"""

from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Hero(Base):
    __tablename__ = "ch05_heroes"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


engine = create_engine(
    "postgresql+psycopg://course:course@localhost:5439/course",
    echo=True,  # print every SQL statement — watch WHEN things happen
)
Base.metadata.create_all(engine)
print("\n========== watch the log lines below ==========\n")

with Session(engine) as session:
    print(">>> session.add(...) x3  (watch: NO SQL happens)")
    session.add(Hero(name="Murderbot"))
    session.add(Hero(name="Breq"))
    session.add(Hero(name="Cordelia"))

    print(">>> running a query  (watch: the INSERTs happen NOW — autoflush)")
    count = session.scalar(select(Hero.id).order_by(Hero.id.desc()).limit(1))

    print(">>> session.commit()  (watch: just COMMIT — the work was already flushed)")
    session.commit()

print("\n========== identity map ==========")
with Session(engine) as session:
    a = session.get(Hero, 1)  # SELECT happens
    b = session.get(Hero, 1)  # NO SELECT — the session already has #1
    print(f"a is b -> {a is b}  (one row, ONE Python object per session)")

    c = session.scalars(select(Hero).where(Hero.name == "Murderbot")).one()
    print(f"a is c -> {a is c}  (even via a totally different query)")

Base.metadata.drop_all(engine)
engine.dispose()
