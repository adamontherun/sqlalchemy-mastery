import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from conftest import DB_URL


@pytest.fixture(scope="module")
def engine():
    # a pool of ONE connection with zero overflow: any leaked session/checkout
    # deadlocks the next test call instantly. Hygiene is enforced by physics.
    engine = create_engine(DB_URL, pool_size=1, max_overflow=0, pool_timeout=2)
    yield engine
    engine.dispose()


@pytest.fixture()
def session_factory(subject, engine):
    subject.Base.metadata.drop_all(engine)
    subject.Base.metadata.create_all(engine)
    yield sessionmaker(engine)
    subject.Base.metadata.drop_all(engine)


def test_create_player_returns_generated_id(subject, session_factory):
    id_a = subject.create_player(session_factory, "ada")
    id_b = subject.create_player(session_factory, "grace")
    assert isinstance(id_a, int) and isinstance(id_b, int)
    assert id_b != id_a


def test_create_player_commits(subject, session_factory):
    player_id = subject.create_player(session_factory, "ada")
    with session_factory() as fresh:
        player = fresh.get(subject.Player, player_id)
        assert player is not None, "player not visible to a new session — commit?"
        assert player.handle == "ada"
        assert player.score == 0


def test_rename_player(subject, session_factory):
    player_id = subject.create_player(session_factory, "ada")
    subject.rename_player(session_factory, player_id, "countess")
    with session_factory() as fresh:
        assert fresh.get(subject.Player, player_id).handle == "countess"


def test_add_score_returns_new_total(subject, session_factory):
    subject.create_player(session_factory, "ada")
    assert subject.add_score(session_factory, "ada", 30) == 30
    assert subject.add_score(session_factory, "ada", 12) == 42


def test_top_players(subject, session_factory):
    for handle, points in [("ada", 90), ("grace", 90), ("alan", 70), ("edsger", 99)]:
        subject.create_player(session_factory, handle)
        subject.add_score(session_factory, handle, points)
    assert subject.top_players(session_factory, 3) == [
        ("edsger", 99),
        ("ada", 90),
        ("grace", 90),
    ]


def test_no_leaked_sessions(subject, session_factory):
    # The pool has exactly one connection. If any function forgot to close
    # its session, this loop cannot complete 20 iterations before timing out.
    for i in range(20):
        subject.create_player(session_factory, f"bot{i}")
    assert len(subject.top_players(session_factory, 20)) == 20
