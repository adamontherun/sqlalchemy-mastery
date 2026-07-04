"""Chapter 1 reference solution."""

from sqlalchemy import Engine, URL, create_engine, text


def make_url() -> URL:
    return URL.create(
        "postgresql+psycopg",
        username="course",
        password="course",
        host="localhost",
        port=5439,
        database="course",
    )


def add_numbers(engine: Engine, a: int, b: int) -> int:
    with engine.connect() as conn:
        return conn.execute(text("SELECT :a + :b"), {"a": a, "b": b}).scalar_one()


def server_major_version(engine: Engine) -> int:
    with engine.connect() as conn:
        num = conn.execute(
            text("SELECT current_setting('server_version_num')::int")
        ).scalar_one()
    return num // 10_000


if __name__ == "__main__":
    engine = create_engine(make_url())
    print("2 + 2 =", add_numbers(engine, 2, 2))
    print("PostgreSQL major version:", server_major_version(engine))
