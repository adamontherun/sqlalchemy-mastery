"""Chapter 11 reference solution."""

from sqlalchemy import ForeignKey, String, func, insert, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
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
    stores = session.scalars(select(Store)).all()
    rows = []
    for store in stores:
        n = len(store.sales)
        total = sum(s.amount_cents for s in store.sales)
        if n:
            rows.append((store.city, n, total))
    rows.sort(key=lambda r: (-r[2], r[0]))
    return rows


def bulk_load(session: Session, cities: list[str], sales_per_store: int) -> None:
    store_ids = session.scalars(
        insert(Store).returning(Store.id, sort_by_parameter_order=True),
        [{"city": city} for city in cities],
    ).all()
    session.execute(
        insert(Sale),
        [
            {"store_id": store_id, "amount_cents": 100 * (i + 1)}
            for store_id in store_ids
            for i in range(sales_per_store)
        ],
    )


def fast_report(session: Session) -> list[tuple[str, int, int]]:
    stmt = (
        select(
            Store.city,
            func.count(Sale.id),
            func.sum(Sale.amount_cents),
        )
        .join_from(Store, Sale)
        .group_by(Store.city)
        .order_by(func.sum(Sale.amount_cents).desc(), Store.city)
    )
    return [(city, n, int(total)) for city, n, total in session.execute(stmt)]
