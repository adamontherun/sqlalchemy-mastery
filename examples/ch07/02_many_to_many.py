"""Many-to-many: the association table pattern.

Run me:  uv run examples/ch07/02_many_to_many.py
"""

from sqlalchemy import Column, ForeignKey, String, Table, create_engine, func, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


# The join table is plain Core — it has no identity of its own, so no class.
post_tags = Table(
    "ch07_post_tags",
    Base.metadata,
    Column("post_id", ForeignKey("ch07_posts.id"), primary_key=True),
    Column("tag_id", ForeignKey("ch07_tags.id"), primary_key=True),
)


class Post(Base):
    __tablename__ = "ch07_posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    tags: Mapped[list["Tag"]] = relationship(secondary=post_tags, back_populates="posts")


class Tag(Base):
    __tablename__ = "ch07_tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    posts: Mapped[list[Post]] = relationship(secondary=post_tags, back_populates="tags")


engine = create_engine("postgresql+psycopg://course:course@localhost:5439/course")
Base.metadata.create_all(engine)

with Session(engine) as session:
    python, sql, war_stories = Tag(name="python"), Tag(name="sql"), Tag(name="war-stories")
    session.add_all(
        [
            Post(title="Why your pool is exhausted", tags=[python, sql, war_stories]),
            Post(title="N+1 queries: a horror story", tags=[sql, war_stories]),
            Post(title="uv in anger", tags=[python]),
        ]
    )
    session.commit()

    # navigate: tag -> posts
    tag = session.scalars(select(Tag).where(Tag.name == "war-stories")).one()
    print("war-stories posts:")
    for post in tag.posts:
        print(f"  - {post.title}")

    # query THROUGH the association: posts per tag, no objects needed
    stmt = (
        select(Tag.name, func.count(post_tags.c.post_id))
        .join_from(Tag, post_tags)
        .group_by(Tag.name)
        .order_by(Tag.name)
    )
    print("\nposts per tag:")
    for name, n in session.execute(stmt):
        print(f"  {name:<12} {n}")

Base.metadata.drop_all(engine)
engine.dispose()
