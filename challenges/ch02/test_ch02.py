import pytest
from conftest import DB_URL
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import QueuePool


@pytest.fixture(scope="module")
def engine(subject):
    engine = subject.make_production_engine(DB_URL)
    yield engine
    engine.dispose()


@pytest.fixture()
def accounts(engine):
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS ch02_accounts"))
        conn.execute(
            text(
                "CREATE TABLE ch02_accounts ("
                " name text PRIMARY KEY,"
                " balance_cents int NOT NULL CHECK (balance_cents >= 0))"
            )
        )
        conn.execute(text("INSERT INTO ch02_accounts VALUES ('alice', 10000), ('bob', 500)"))
    yield
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS ch02_accounts"))


def test_engine_configuration(engine):
    pool = engine.pool
    assert isinstance(pool, QueuePool)
    assert pool.size() == 10, "pool_size should be 10"
    assert pool._max_overflow == 5, "max_overflow should be 5"
    assert engine.pool._pre_ping is True, "pool_pre_ping should be on"
    assert engine.pool._recycle == 1800, "pool_recycle should be 1800 seconds"


def test_successful_transfer(subject, engine, accounts):
    subject.transfer(engine, "alice", "bob", 2500)
    assert subject.account_balance(engine, "alice") == 7500
    assert subject.account_balance(engine, "bob") == 3000


def test_failed_transfer_changes_nothing(subject, engine, accounts):
    # bob has 500; sending 9999 must violate the CHECK on his debit...
    with pytest.raises(IntegrityError):
        subject.transfer(engine, "bob", "alice", 9999)
    # ...and alice must NOT have received phantom money.
    assert subject.account_balance(engine, "alice") == 10000
    assert subject.account_balance(engine, "bob") == 500
