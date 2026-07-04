"""Types, constraints, defaults — the vocabulary of a well-built model.

Run me:  uv run examples/ch04/02_types_and_constraints.py
"""

import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.schema import CreateTable


class Base(DeclarativeBase):
    pass


class OrderStatus(enum.Enum):
    pending = "pending"
    shipped = "shipped"
    cancelled = "cancelled"


class Order(Base):
    __tablename__ = "ch04_orders"
    __table_args__ = (
        CheckConstraint("total_cents >= 0", name="positive_total"),
        UniqueConstraint("customer_email", "reference", name="uq_customer_reference"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Mapped[str] alone -> VARCHAR (unbounded on PG); give a length when you
    # mean one, or Text for prose.
    reference: Mapped[str] = mapped_column(String(20))
    customer_email: Mapped[str] = mapped_column(String(255), index=True)
    note: Mapped[str | None] = mapped_column(Text)

    # Money: NEVER Float. Numeric -> Decimal in Python, exact in SQL.
    total_cents: Mapped[int]
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    # Python enum -> native PostgreSQL ENUM type (see the DDL below)
    status: Mapped[OrderStatus] = mapped_column(default=OrderStatus.pending)

    # JSONB, dialect-specific and glorious
    metadata_blob: Mapped[dict | None] = mapped_column("metadata", JSONB)

    # timestamps: server_default runs IN the database -> correct even if
    # rows are inserted by psql, a cron job, or another service entirely.
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


engine = create_engine("postgresql+psycopg://course:course@localhost:5439/course")
# __table__ is typed as the more general FromClause; it's always a Table
# for a declarative class, which is what CreateTable actually expects.
print(CreateTable(Order.__table__).compile(engine))  # type: ignore[arg-type]

Base.metadata.create_all(engine)
with Session(engine) as session:
    order = Order(
        reference="A-1001",
        customer_email="ada@example.com",
        total_cents=4200,
        unit_price=Decimal("21.00"),
        metadata_blob={"gift": True},
    )
    session.add(order)
    session.commit()
    print(f"status default applied: {order.status}")
    print(f"server-side created_at: {order.created_at}")

Base.metadata.drop_all(engine)
engine.dispose()
