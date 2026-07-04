"""Proof that the rollback-per-test pattern isolates tests — even with commits.

Run me:  uv run pytest examples/ch10 -v
"""

from conftest import Widget
from sqlalchemy import func, select


def test_writes_and_commits(db_session):
    db_session.add(Widget(name="gizmo"))
    db_session.commit()  # a REAL commit in app code terms
    db_session.add(Widget(name="doohickey"))
    db_session.commit()

    count = db_session.scalar(select(func.count(Widget.id)))
    assert count == 2


def test_sees_none_of_the_previous_tests_data(db_session):
    # If the commits above had truly persisted, this would be 2.
    count = db_session.scalar(select(func.count(Widget.id)))
    assert count == 0


def test_rollback_mid_test_works_too(db_session):
    db_session.add(Widget(name="oops"))
    db_session.rollback()  # app code rolling back: also fine
    assert db_session.scalar(select(func.count(Widget.id))) == 0


async def test_async_flavor(async_db_session):
    async_db_session.add(Widget(name="async gizmo"))
    await async_db_session.commit()
    count = await async_db_session.scalar(select(func.count(Widget.id)))
    assert count == 1


async def test_async_isolation(async_db_session):
    count = await async_db_session.scalar(select(func.count(Widget.id)))
    assert count == 0
