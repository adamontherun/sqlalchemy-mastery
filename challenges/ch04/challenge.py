"""Chapter 4 challenge — model a product catalog to spec.

Make `uv run pytest challenges/ch04` pass.

The tests inspect your model's generated Table — names, types, nullability,
constraints, defaults — so this is about *declaring* precisely, not querying.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# Build a model class named `Product` with __tablename__ "ch04_products":
#
#   id          int, primary key
#   sku         str, max length 32, NOT NULL, unique
#   name        str, max length 200, NOT NULL
#   description str, unbounded text, NULLABLE
#   price       Decimal (Numeric(10, 2)), NOT NULL
#   stock       int, NOT NULL, Python-side default 0
#   created_at  datetime, NOT NULL, DATABASE-side default now()
#
# plus a CHECK constraint  stock >= 0  named (via the convention) so that
# the final name is "ck_ch04_products_non_negative_stock".
#
# Delete this comment and declare it below.


class Product(Base):
    __tablename__ = "ch04_products"

    # your columns here...
    raise NotImplementedError("declare the Product model")
