"""Upserts: PostgreSQL's ON CONFLICT through SQLAlchemy.

Run me:  uv run examples/ch06/03_upsert.py
"""

from sqlalchemy import String, create_engine, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Setting(Base):
    __tablename__ = "ch06_settings"
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(String(500))


engine = create_engine("postgresql+psycopg://course:course@localhost:5439/course")
Base.metadata.create_all(engine)


# The generic insert() is portable; the DIALECT insert knows PostgreSQL tricks.
def upsert_setting(session: Session, key: str, value: str) -> None:
    stmt = pg_insert(Setting).values(key=key, value=value)
    stmt = stmt.on_conflict_do_update(
        index_elements=[Setting.key],
        set_={"value": stmt.excluded.value},  # EXCLUDED = the row that clashed
    )
    session.execute(stmt)


with Session(engine) as session:
    upsert_setting(session, "theme", "light")
    upsert_setting(session, "lang", "en")
    upsert_setting(session, "theme", "dark")  # same key: updates, no error
    session.commit()

    for setting in session.scalars(select(Setting).order_by(Setting.key)):
        print(f"  {setting.key} = {setting.value}")

print("\n'theme' was inserted then upserted — one row, latest value, zero try/except.")

Base.metadata.drop_all(engine)
engine.dispose()
