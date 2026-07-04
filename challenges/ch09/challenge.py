"""Chapter 9 challenge — write a migration by hand.

Make `uv run pytest challenges/ch09` pass.

Autogenerate writes most migrations, but you must be able to write (and
correct!) the op directives yourself — that's exactly what you do whenever
autogenerate hits one of its blind spots. The tests hand you a live
`Operations` object bound to a real connection; implement upgrade() and
downgrade() as you would inside a migration file.
"""

import sqlalchemy as sa
from alembic.operations import Operations


def upgrade(op: Operations) -> None:
    """Create the schema for a URL shortener, exactly:

    Table "ch09_links":
      * id          INTEGER, autoincrementing primary key
      * slug        VARCHAR(32), NOT NULL
      * target      VARCHAR(2000), NOT NULL
      * clicks      INTEGER, NOT NULL, server default '0'

    Plus:
      * a UNIQUE constraint on slug named  uq_ch09_links_slug
      * an index on clicks named           ix_ch09_links_clicks

    Use op.create_table / op.create_unique_constraint / op.create_index
    (or declare the constraint inline in create_table — your call, as long
    as the names match).
    """
    raise NotImplementedError


def downgrade(op: Operations) -> None:
    """Undo upgrade() completely — the database must look untouched.
    (Dropping the table drops its constraints and indexes with it.)
    """
    raise NotImplementedError
