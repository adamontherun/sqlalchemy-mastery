import pytest
from sqlalchemy import URL, create_engine


@pytest.fixture(scope="module")
def engine(subject):
    engine = create_engine(subject.make_url())
    yield engine
    engine.dispose()


def test_make_url_is_a_url_object(subject):
    url = subject.make_url()
    assert isinstance(url, URL), "Return a URL from URL.create(), not a string"
    assert url.drivername == "postgresql+psycopg"
    assert url.host == "localhost"
    assert url.port == 5439
    assert url.database == "course"


def test_url_actually_connects(engine):
    with engine.connect():
        pass  # checking out a connection is proof enough


def test_add_numbers(subject, engine):
    assert subject.add_numbers(engine, 40, 2) == 42
    assert subject.add_numbers(engine, -5, 5) == 0


def test_add_numbers_uses_bound_parameters(subject, engine):
    # A string like "little bobby tables" would explode an f-string query
    # into a syntax error; bound parameters make this a non-event.
    assert subject.add_numbers(engine, 2, 2) == 4


def test_server_major_version(subject, engine):
    assert subject.server_major_version(engine) == 17
