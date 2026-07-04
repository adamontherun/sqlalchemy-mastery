import pytest
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session

from conftest import DB_URL


@pytest.fixture(scope="module")
def engine():
    engine = create_engine(DB_URL)
    yield engine
    engine.dispose()


@pytest.fixture()
def counter(engine):
    counts = {"n": 0}

    def count(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("SELECT"):
            counts["n"] += 1

    event.listen(engine, "before_cursor_execute", count)
    yield counts
    event.remove(engine, "before_cursor_execute", count)


@pytest.fixture()
def session(subject, engine):
    subject.Base.metadata.drop_all(engine)
    subject.Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all([
            subject.Team(name="Arsenal", players=[
                subject.Player(name="Saka", goals=16),
                subject.Player(name="Havertz", goals=13),
                subject.Player(name="Rice", goals=7),
            ]),
            subject.Team(name="Liverpool", players=[
                subject.Player(name="Salah", goals=28),
                subject.Player(name="Gakpo", goals=10),
            ]),
            subject.Team(name="Brighton", players=[]),
        ])
        session.commit()
        session.expire_all()  # force everything to load fresh in the tests
        yield session
    subject.Base.metadata.drop_all(engine)


def test_relationships_are_wired(subject, session):
    team = session.scalars(
        select(subject.Team).where(subject.Team.name == "Arsenal")
    ).one()
    assert {p.name for p in team.players} == {"Saka", "Havertz", "Rice"}
    assert team.players[0].team is team, "back_populates should link both ways"


def test_rosters_content(subject, session, counter):
    result = subject.rosters(session)
    assert result == {
        "Arsenal": ["Saka", "Havertz", "Rice"],
        "Liverpool": ["Salah", "Gakpo"],
        "Brighton": [],
    }


def test_rosters_query_budget(subject, session, counter):
    subject.rosters(session)
    assert counter["n"] <= 2, (
        f"rosters() used {counter['n']} SELECTs — that's an N+1. "
        "Load the collection eagerly (selectinload)."
    )


def test_top_scorer_teams_content(subject, session, counter):
    assert subject.top_scorer_teams(session, 10) == [
        ("Salah", "Liverpool"),
        ("Saka", "Arsenal"),
        ("Havertz", "Arsenal"),
        ("Gakpo", "Liverpool"),
    ]


def test_top_scorer_teams_query_budget(subject, session, counter):
    subject.top_scorer_teams(session, 10)
    assert counter["n"] == 1, (
        f"top_scorer_teams() used {counter['n']} SELECTs — "
        "one joinedload'ed query should do it."
    )
