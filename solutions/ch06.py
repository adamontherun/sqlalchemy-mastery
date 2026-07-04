"""Chapter 6 reference solution."""

import datetime

from sqlalchemy import ForeignKey, String, func, select, update
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class Member(Base):
    __tablename__ = "ch06_members"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    joined: Mapped[datetime.date]


class Loan(Base):
    __tablename__ = "ch06_loans"
    id: Mapped[int] = mapped_column(primary_key=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("ch06_members.id"))
    book_title: Mapped[str] = mapped_column(String(200))
    due: Mapped[datetime.date]
    returned: Mapped[bool] = mapped_column(default=False)


def overdue_titles(session: Session, today: datetime.date) -> list[str]:
    stmt = (
        select(Loan.book_title)
        .where(Loan.returned.is_(False), Loan.due < today)
        .order_by(Loan.book_title)
    )
    return list(session.scalars(stmt))


def _loan_counts_stmt():
    return (
        select(Member.name, func.count(Loan.id).label("n"))
        .join_from(Member, Loan)
        .group_by(Member.name)
        .order_by(func.count(Loan.id).desc(), Member.name)
    )


def member_loan_counts(session: Session) -> list[tuple[str, int]]:
    return [tuple(row) for row in session.execute(_loan_counts_stmt())]


def busiest_member(session: Session) -> str:
    return session.execute(_loan_counts_stmt().limit(1)).scalar_one()


def mark_returned(session: Session, titles: list[str]) -> int:
    result = session.execute(
        update(Loan).where(Loan.book_title.in_(titles)).values(returned=True)
    )
    session.commit()
    return result.rowcount
