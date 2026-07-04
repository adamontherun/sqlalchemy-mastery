"""The models this demo project migrates. Edit me, autogenerate, repeat.

This file is the single source of truth for the schema; Alembic compares it
to the live database and writes the diff as a migration.
"""

from datetime import datetime

from sqlalchemy import ForeignKey, MetaData, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# ch04's lesson, applied where it matters most: without this, autogenerate
# cannot name (and therefore cannot later drop) your constraints.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Workspace(Base):
    __tablename__ = "ch09_workspaces"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    documents: Mapped[list["Document"]] = relationship(back_populates="workspace")


class Document(Base):
    __tablename__ = "ch09_documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(300))
    workspace_id: Mapped[int] = mapped_column(ForeignKey("ch09_workspaces.id"))

    # Added after the first release — see the second migration in versions/.
    # server_default matters: the table already has rows when this lands.
    word_count: Mapped[int] = mapped_column(server_default="0")

    workspace: Mapped[Workspace] = relationship(back_populates="documents")
