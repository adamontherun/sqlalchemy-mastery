import pytest
from conftest import DB_URL
from sqlalchemy import create_engine, text

SEED = [
    {"title": "The Left Hand of Darkness", "genre": "sf", "price": 18.99},
    {"title": "The Dispossessed", "genre": "sf", "price": 17.25},
    {"title": "A Memory Called Empire", "genre": "sf", "price": 16.00},
    {"title": "Piranesi", "genre": "fantasy", "price": 14.99},
    {"title": "A Wizard of Earthsea", "genre": "fantasy", "price": 15.50},
]


@pytest.fixture(scope="module")
def engine():
    engine = create_engine(DB_URL)
    yield engine
    engine.dispose()


@pytest.fixture()
def shop(subject, engine):
    subject.metadata.drop_all(engine)
    subject.metadata.create_all(engine)
    yield
    subject.metadata.drop_all(engine)


def test_add_books_returns_rowcount(subject, engine, shop):
    assert subject.add_books(engine, SEED) == 5


def test_add_books_actually_commits(subject, engine, shop):
    subject.add_books(engine, SEED)
    with engine.connect() as conn:  # a NEW connection must see the rows
        n = conn.execute(text("SELECT count(*) FROM ch03_shop_books")).scalar_one()
    assert n == 5, "Rows not visible from a fresh connection — did you commit?"


def test_titles_in_genre_sorted(subject, engine, shop):
    subject.add_books(engine, SEED)
    assert subject.titles_in_genre(engine, "fantasy") == [
        "A Wizard of Earthsea",
        "Piranesi",
    ]
    assert subject.titles_in_genre(engine, "cookbooks") == []


def test_average_price_by_genre(subject, engine, shop):
    subject.add_books(engine, SEED)
    result = subject.average_price_by_genre(engine)
    assert result == {"sf": 17.41, "fantasy": 15.25}


def test_apply_discount_returns_new_prices(subject, engine, shop):
    subject.add_books(engine, SEED)
    rows = subject.apply_discount(engine, "fantasy", 10)
    assert sorted(rows) == [
        ("A Wizard of Earthsea", 13.95),
        ("Piranesi", 13.49),
    ]
    # and the change must be durable:
    with engine.connect() as conn:
        piranesi = conn.execute(
            text("SELECT price FROM ch03_shop_books WHERE title = 'Piranesi'")
        ).scalar_one()
    assert float(piranesi) == 13.49
