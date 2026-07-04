import pytest
from conftest import DB_URL
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

CITIES = ["Lisbon", "Nairobi", "Osaka", "Denver", "Tallinn"]


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
        yield session
    subject.Base.metadata.drop_all(engine)


@pytest.fixture()
def counter(engine):
    counts = {"insert": 0, "select": 0}

    def count(conn, cursor, statement, parameters, context, executemany):
        word = statement.lstrip().split()[0].upper()
        if word == "INSERT":
            counts["insert"] += 1
        elif word == "SELECT":
            counts["select"] += 1

    event.listen(engine, "before_cursor_execute", count)
    yield counts
    event.remove(engine, "before_cursor_execute", count)


def test_bulk_load_shape(subject, session):
    subject.bulk_load(session, CITIES, sales_per_store=3)
    session.commit()
    report = subject.naive_report(session)
    assert len(report) == 5
    assert all(n == 3 and total == 600 for _, n, total in report)


def test_bulk_load_budget(subject, session, counter):
    subject.bulk_load(session, CITIES, sales_per_store=10)
    session.commit()
    assert counter["insert"] <= 2, (
        f"bulk_load used {counter['insert']} INSERT statements — "
        "pass lists of dicts to insert(), don't add() objects in a loop"
    )


def test_fast_report_matches_oracle(subject, session):
    subject.bulk_load(session, CITIES, sales_per_store=7)
    session.commit()
    assert subject.fast_report(session) == subject.naive_report(session)


def test_fast_report_budget(subject, session, counter):
    subject.bulk_load(session, CITIES, sales_per_store=7)
    session.commit()
    session.expire_all()
    before = counter["select"]
    subject.fast_report(session)
    used = counter["select"] - before
    assert used <= 2, (
        f"fast_report used {used} SELECTs — aggregate in SQL "
        "(func.count/func.sum + group_by), don't touch store.sales"
    )
