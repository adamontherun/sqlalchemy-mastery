"""Chapter 1 challenge — first contact.

Make `uv run pytest challenges/ch01` pass using only Chapter 1 material:
create_engine, URL.create, text(), bound parameters, and the Result API.

Rules of the game (all chapters):
  * Replace each `raise NotImplementedError` with working code.
  * Never build SQL strings with f-strings — always bound parameters.
"""

from sqlalchemy import URL, Engine, create_engine, text


def make_url() -> URL:
    """Build the course database URL *programmatically* with URL.create().

    Dialect+driver postgresql+psycopg, user/password course/course,
    host localhost, port 5439, database course.

    URL.create() beats string concatenation the moment a password contains
    '@' or '/' — it handles escaping for you.
    """
    raise NotImplementedError


def add_numbers(engine: Engine, a: int, b: int) -> int:
    """Ask PostgreSQL — not Python — what a + b is.

    Use text() with bound parameters and return the single scalar result.
    """
    raise NotImplementedError


def server_major_version(engine: Engine) -> int:
    """Return the server's major version (e.g. 17) as an int.

    Hint: `current_setting('server_version_num')` returns e.g. '170010';
    major = that as int, divided by 10_000.
    """
    raise NotImplementedError


if __name__ == "__main__":
    engine = create_engine(make_url())
    print("2 + 2 =", add_numbers(engine, 2, 2))
    print("PostgreSQL major version:", server_major_version(engine))
