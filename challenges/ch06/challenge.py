"""Chapter 6 challenge — ORM querying on a library's loan desk.

Make `uv run pytest challenges/ch06` pass.

Models and seed data are provided; write the queries. Everything must be
computed by the database — tests will not accept Python-side loops over
all rows (we can't police it mechanically, but your future self can).
"""

import datetime

from sqlalchemy import ForeignKey, String, func, select
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
    """Titles of unreturned loans past their due date, alphabetical."""
    raise NotImplementedError


def member_loan_counts(session: Session) -> list[tuple[str, int]]:
    """[(member_name, number_of_loans), ...] for members WITH at least one
    loan, most loans first, ties by name. JOIN + GROUP BY, one query.
    """
    raise NotImplementedError


def busiest_member(session: Session) -> str:
    """Name of the member with the most loans (unique in the test data).
    Reuse your one query — no fetching-everything-and-picking-in-Python.
    """
    raise NotImplementedError


def mark_returned(session: Session, titles: list[str]) -> int:
    """Set returned=True for every loan whose title is in `titles`
    (bulk UPDATE with IN — one statement) and return how many rows changed.
    Commit before returning.
    """
    raise NotImplementedError
