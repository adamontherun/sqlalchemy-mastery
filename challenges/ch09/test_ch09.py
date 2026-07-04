import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text

from conftest import DB_URL


@pytest.fixture()
def engine():
    engine = create_engine(DB_URL)
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS ch09_links"))
    yield engine
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS ch09_links"))
    engine.dispose()


@pytest.fixture()
def migrated(subject, engine):
    with engine.begin() as conn:
        subject.upgrade(Operations(MigrationContext.configure(conn)))
    yield engine


def test_upgrade_creates_table_and_columns(subject, migrated):
    insp = inspect(migrated)
    cols = {c["name"]: c for c in insp.get_columns("ch09_links")}
    assert set(cols) == {"id", "slug", "target", "clicks"}
    assert isinstance(cols["slug"]["type"], sa.String) and cols["slug"]["type"].length == 32
    assert cols["slug"]["nullable"] is False
    assert cols["target"]["type"].length == 2000
    assert cols["clicks"]["nullable"] is False
    assert cols["clicks"]["default"] is not None, "clicks needs a server default"


def test_upgrade_names_the_constraints(subject, migrated):
    insp = inspect(migrated)
    uqs = {u["name"] for u in insp.get_unique_constraints("ch09_links")}
    ixs = {i["name"] for i in insp.get_indexes("ch09_links")}
    assert "uq_ch09_links_slug" in uqs, f"unique constraints found: {uqs}"
    assert "ix_ch09_links_clicks" in ixs, f"indexes found: {ixs}"


def test_server_default_works(subject, migrated):
    with migrated.begin() as conn:
        conn.execute(text(
            "INSERT INTO ch09_links (slug, target) VALUES ('gh', 'https://github.com')"
        ))
        clicks = conn.execute(text("SELECT clicks FROM ch09_links")).scalar_one()
    assert clicks == 0


def test_downgrade_removes_everything(subject, migrated):
    with migrated.begin() as conn:
        subject.downgrade(Operations(MigrationContext.configure(conn)))
    assert not inspect(migrated).has_table("ch09_links")


def test_up_down_up_is_stable(subject, engine):
    # the mark of a trustworthy migration: it cycles
    for _ in range(2):
        with engine.begin() as conn:
            subject.upgrade(Operations(MigrationContext.configure(conn)))
        with engine.begin() as conn:
            subject.downgrade(Operations(MigrationContext.configure(conn)))
    assert not inspect(engine).has_table("ch09_links")
