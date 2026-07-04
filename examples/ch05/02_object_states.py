"""The four lives of an ORM object: transient, pending, persistent, detached.

Run me:  uv run examples/ch05/02_object_states.py
"""

from sqlalchemy import String, create_engine, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Ship(Base):
    __tablename__ = "ch05_ships"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


def state_of(obj) -> str:
    ins = inspect(obj)
    for state in ("transient", "pending", "persistent", "detached"):
        if getattr(ins, state):
            return state
    return "?"


engine = create_engine("postgresql+psycopg://course:course@localhost:5439/course")
Base.metadata.create_all(engine)

ship = Ship(name="Rocinante")
print(f"constructed:          {state_of(ship):<11} (plain Python object, no session)")

session = Session(engine)
session.add(ship)
print(f"after session.add():  {state_of(ship):<11} (queued for INSERT, no id yet: {ship.id})")

session.flush()
print(f"after flush():        {state_of(ship):<11} (INSERT ran, id={ship.id} — but NOT committed)")

session.commit()
print(f"after commit():       {state_of(ship):<11} (transaction closed)")

session.close()
print(f"after close():        {state_of(ship):<11} (object lives on, session doesn't)")

# Detached objects can rejoin a new session:
with Session(engine) as session2:
    ship = session2.merge(ship)
    print(f"after merge():        {state_of(ship):<11} (adopted by a new session)")

Base.metadata.drop_all(engine)
engine.dispose()
