# SQLAlchemy Mastery

A hands-on course on modern SQLAlchemy (2.0-style API): sync, async, connections,
querying, relationships, Alembic, testing, performance, and FastAPI integration.

## The book

Open **[book/index.html](book/index.html)** in your browser. It's a self-contained
static HTML book — no build step, works offline, light and dark mode.

## Setup

You need [Docker](https://docs.docker.com/get-docker/) and [uv](https://docs.astral.sh/uv/).

```sh
docker compose up -d   # starts PostgreSQL 17 on localhost:5439
uv sync                # installs Python 3.13 + all dependencies
```

The database is `postgresql://course:course@localhost:5439/course`. Port **5439**
is used on the host so it never collides with a locally installed Postgres.

## Running examples

Every chapter has runnable scripts under `examples/`:

```sh
uv run examples/ch02/01_first_connection.py
```

## Doing challenges

Every chapter has a challenge under `challenges/` — a skeleton file with failing
tests. Edit the skeleton until the tests pass:

```sh
uv run pytest challenges/ch03
```

Reference solutions live in `solutions/` — no peeking until the tests pass.

## Resetting the database

Examples clean up after themselves, but if you ever want a pristine database:

```sh
docker compose down -v && docker compose up -d
```
