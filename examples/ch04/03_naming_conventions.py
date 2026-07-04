"""The naming convention that will save your migrations.

Run me:  uv run examples/ch04/03_naming_conventions.py
"""

from sqlalchemy import ForeignKey, MetaData, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.schema import CreateTable

# Without this, PostgreSQL invents names like "ch04_pets_owner_id_fkey" and
# SQLAlchemy knows constraints only as "None" — so Alembic can't drop or
# alter them later. Set the convention ONCE, on day one, in your Base.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Owner(Base):
    __tablename__ = "ch04_owners"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)


class Pet(Base):
    __tablename__ = "ch04_pets"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    owner_id: Mapped[int] = mapped_column(ForeignKey("ch04_owners.id"))


engine = create_engine("postgresql+psycopg://course:course@localhost:5439/course")

print("Every constraint now has a deterministic, Alembic-friendly name:\n")
print(CreateTable(Owner.__table__).compile(engine))
print(CreateTable(Pet.__table__).compile(engine))
engine.dispose()
