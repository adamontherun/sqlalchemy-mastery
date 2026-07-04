from decimal import Decimal

import pytest
from sqlalchemy import CheckConstraint, Numeric, String, Text, create_engine, select

from conftest import DB_URL


@pytest.fixture(scope="module")
def table(subject):
    return subject.Product.__table__


def test_table_name(table):
    assert table.name == "ch04_products"


def test_primary_key(table):
    assert [c.name for c in table.primary_key.columns] == ["id"]


def test_sku(table):
    sku = table.c.sku
    assert isinstance(sku.type, String) and sku.type.length == 32
    assert sku.nullable is False
    assert sku.unique or any(
        {c.name for c in con.columns} == {"sku"}
        for con in table.constraints
        if con.__class__.__name__ == "UniqueConstraint"
    ), "sku must be unique"


def test_description_is_nullable_text(table):
    assert isinstance(table.c.description.type, Text)
    assert table.c.description.nullable is True


def test_price_is_numeric(table):
    assert isinstance(table.c.price.type, Numeric)
    assert (table.c.price.type.precision, table.c.price.type.scale) == (10, 2)
    assert not isinstance(table.c.price.type, (type(None),))


def test_stock_default_is_python_side(table):
    assert table.c.stock.default is not None, "stock needs default=0"
    assert table.c.stock.default.arg == 0
    assert table.c.stock.server_default is None, "spec says Python-side default"


def test_created_at_default_is_server_side(table):
    assert table.c.created_at.server_default is not None, (
        "created_at needs server_default=func.now()"
    )


def test_check_constraint_is_named(table):
    names = {c.name for c in table.constraints if isinstance(c, CheckConstraint)}
    assert "ck_ch04_products_non_negative_stock" in names, (
        f"expected the naming convention to produce "
        f"ck_ch04_products_non_negative_stock; found {names or 'no CHECKs'}"
    )


def test_model_round_trips(subject):
    engine = create_engine(DB_URL)
    subject.Base.metadata.create_all(engine)
    try:
        from sqlalchemy.orm import Session

        with Session(engine) as session:
            session.add(subject.Product(
                sku="TEA-001", name="Gunpowder tea", price=Decimal("12.50"),
            ))
            session.commit()
            product = session.scalars(select(subject.Product)).one()
            assert product.stock == 0, "default should fill stock"
            assert product.created_at is not None, "server default should fill created_at"
    finally:
        subject.Base.metadata.drop_all(engine)
        engine.dispose()
