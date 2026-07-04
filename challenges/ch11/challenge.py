"""Chapter 11 challenge — fix the slow report.

Make `uv run pytest challenges/ch11` pass.

Below is a working but disastrous implementation of a sales report
(naive_report). Your job: reimplement it as fast_report() with the SAME
output under a budget of AT MOST 2 SQL statements — and implement
bulk_load() to seed data with AT MOST 2 statements as well.

The tests count every statement. naive_report is kept as your oracle:
fast_report(session) must return exactly what naive_report(session) returns.
"""

from sqlalchemy import ForeignKey, String, func, select
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, Session, mapped_column, relationship, selectinload,
)


class Base(DeclarativeBase):
    pass


class Store(Base):
    __tablename__ = "ch11_stores"
    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str] = mapped_column(String(100))
    sales: Mapped[list["Sale"]] = relationship(back_populates="store")


class Sale(Base):
    __tablename__ = "ch11_sales"
    id: Mapped[int] = mapped_column(primary_key=True)
    amount_cents: Mapped[int]
    store_id: Mapped[int] = mapped_column(ForeignKey("ch11_stores.id"))
    store: Mapped[Store] = relationship(back_populates="sales")


def naive_report(session: Session) -> list[tuple[str, int, int]]:
    """[(city, number_of_sales, total_cents), ...] sorted by total desc,
    ties broken by city ascending.

    Correct output, catastrophic execution: one query per store (N+1) and
    all the summing done in Python. DO NOT EDIT — this is your oracle.
    """
    stores = session.scalars(select(Store)).all()
    rows = []
    for store in stores:
        n = len(store.sales)                      # lazy load per store!
        total = sum(s.amount_cents for s in store.sales)
        if n:
            rows.append((store.city, n, total))
    rows.sort(key=lambda r: (-r[2], r[0]))
    return rows


def bulk_load(session: Session, cities: list[str], sales_per_store: int) -> None:
    """Create one Store per city plus `sales_per_store` Sales each
    (amount_cents = 100 * (index+1) within each store, i.e. 100, 200, ...).

    Budget: AT MOST 2 INSERT statements total. Hint: insertmanyvalues with
    RETURNING gives you the store ids for the sales dicts.
    """
    raise NotImplementedError


def fast_report(session: Session) -> list[tuple[str, int, int]]:
    """Same result as naive_report, budget: AT MOST 2 SELECT statements.
    Make the DATABASE do the counting and summing.
    """
    raise NotImplementedError
