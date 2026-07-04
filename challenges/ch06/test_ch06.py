import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from conftest import DB_URL

TODAY = datetime.date(2026, 7, 1)


@pytest.fixture(scope="module")
def engine():
    engine = create_engine(DB_URL)
    yield engine
    engine.dispose()


@pytest.fixture()
def session(subject, engine):
    subject.Base.metadata.drop_all(engine)
    subject.Base.metadata.create_all(engine)
    with Session(engine) as session:
        ada = subject.Member(name="Ada", joined=datetime.date(2024, 1, 15))
        grace = subject.Member(name="Grace", joined=datetime.date(2025, 3, 2))
        alan = subject.Member(name="Alan", joined=datetime.date(2025, 11, 20))
        session.add_all([ada, grace, alan])
        session.flush()
        session.add_all([
            subject.Loan(member_id=ada.id, book_title="Gödel, Escher, Bach",
                         due=datetime.date(2026, 6, 12)),
            subject.Loan(member_id=ada.id, book_title="The Art of Computer Programming",
                         due=datetime.date(2026, 7, 20)),
            subject.Loan(member_id=ada.id, book_title="A Pattern Language",
                         due=datetime.date(2026, 5, 1), returned=True),
            subject.Loan(member_id=grace.id, book_title="The Mythical Man-Month",
                         due=datetime.date(2026, 6, 28)),
        ])
        session.commit()
        yield session
    subject.Base.metadata.drop_all(engine)


def test_overdue_titles(subject, session):
    assert subject.overdue_titles(session, TODAY) == [
        "Gödel, Escher, Bach",
        "The Mythical Man-Month",
    ]


def test_member_loan_counts(subject, session):
    assert subject.member_loan_counts(session) == [("Ada", 3), ("Grace", 1)]


def test_busiest_member(subject, session):
    assert subject.busiest_member(session) == "Ada"


def test_mark_returned(subject, session):
    changed = subject.mark_returned(
        session, ["Gödel, Escher, Bach", "The Mythical Man-Month", "Nonexistent"]
    )
    assert changed == 2
    assert subject.overdue_titles(session, TODAY) == []
