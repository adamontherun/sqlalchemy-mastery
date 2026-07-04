"""Chapter 9 reference solution."""

import sqlalchemy as sa
from alembic.operations import Operations


def upgrade(op: Operations) -> None:
    op.create_table(
        "ch09_links",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("slug", sa.String(32), nullable=False),
        sa.Column("target", sa.String(2000), nullable=False),
        sa.Column("clicks", sa.Integer, nullable=False, server_default="0"),
        sa.UniqueConstraint("slug", name="uq_ch09_links_slug"),
    )
    op.create_index("ix_ch09_links_clicks", "ch09_links", ["clicks"])


def downgrade(op: Operations) -> None:
    op.drop_table("ch09_links")  # takes its constraints and indexes with it
