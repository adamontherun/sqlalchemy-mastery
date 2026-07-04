"""Your first mapped class — and what it generates underneath.

Run me:  uv run examples/ch04/01_first_model.py
"""

from datetime import datetime

from sqlalchemy import String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "ch04_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    nickname: Mapped[str | None]  # Optional in Python == NULLable in SQL
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r})"


# Every model *is* a Core Table underneath — nothing from ch03 was wasted:
print("The generated Table object:")
print(f"  name:    {User.__table__.name}")
print(f"  columns: {[c.name for c in User.__table__.columns]}")
print(f"  email nullable? {User.__table__.c.email.nullable}")
print(f"  nickname nullable? {User.__table__.c.nickname.nullable}")

engine = create_engine("postgresql+psycopg://course:course@localhost:5439/course")
Base.metadata.create_all(engine)

with Session(engine) as session:
    session.add(User(name="Ada Lovelace", email="ada@example.com"))
    session.add(User(name="Grace Hopper", email="grace@example.com", nickname="Amazing Grace"))
    session.commit()

    # the same select() from chapter 3 — now with a class instead of a Table
    users = session.scalars(select(User).order_by(User.name)).all()
    for user in users:
        print(f"loaded: {user!r}  created_at={user.created_at:%Y-%m-%d %H:%M}")

Base.metadata.drop_all(engine)
engine.dispose()
