# SQLAlchemy Mastery

A hands-on course on modern SQLAlchemy (2.0-style API): sync, async, connections,
querying, relationships, Alembic, testing, performance, and FastAPI integration.

**[Read the book](https://adamontherun.github.io/sqlalchemy-mastery/)** · [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/adamontherun/sqlalchemy-mastery)

This repo is two things: **the book** (prose you read) and **the code** (examples
and challenges you run). Reading needs nothing installed; running needs an
environment. Every chapter in the book links to Codespaces directly, so you can
jump from a page you're reading straight into a terminal with Postgres already up.

## The book

Open **[book/index.html](book/index.html)** in your browser, or read the
published copy above. It's a self-contained static HTML book: no build
step, works offline, light and dark mode. It doesn't contain any of the
runnable code itself — that lives in `examples/`, `challenges/`, and
`solutions/` below, which is why you need one of the environments in
"Setup" to actually run anything the book shows you.

## Setup

Two ways to get a working environment:

**GitHub Codespaces** — click the badge above. It opens a full dev
environment with the exact same PostgreSQL 17 this course teaches against,
already running. Once it's ready, run `uv sync` if it wasn't run for you
automatically, then jump to "Running examples" below.

**Locally** — you need [Docker](https://docs.docker.com/get-docker/) and
[uv](https://docs.astral.sh/uv/):

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

Every chapter has a challenge under `challenges/`: a skeleton file with failing
tests. Edit the skeleton until the tests pass:

```sh
uv run pytest challenges/ch03
```

Reference solutions live in `solutions/`. No peeking until the tests pass.

## Resetting the database

Examples clean up after themselves, but if you ever want a pristine database:

```sh
docker compose down -v && docker compose up -d
```
