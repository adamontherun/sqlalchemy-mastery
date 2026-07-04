# SQLAlchemy Mastery

A free, hands-on micro-course on modern SQLAlchemy (2.0-style API) — engines,
sessions, querying, async, Alembic, testing, performance, and a real FastAPI
service, taught against a real PostgreSQL 17 database rather than a toy.

[![Read the Book](https://img.shields.io/badge/📖_Read_the_Book-adamontherun.github.io-c0392b)](https://adamontherun.github.io/sqlalchemy-mastery/)

This repo is two things: **the book** (12 chapters of prose, nothing to
install) and **the code** (runnable examples and failing-test challenges,
which need an environment). Every chapter in the book links straight back to
Codespaces, so you're never more than one click from a terminal with Postgres
already running.

## What's covered

- **Part I · Foundations** — engines, connection pools, querying with Core
- **Part II · The ORM** — declarative models, the Session, querying, relationships
- **Part III · Async** — `AsyncSession`, asyncpg, and every `MissingGreenlet` trap
- **Part IV · Production** — Alembic migrations, testing, performance, FastAPI integration

## Setup

Don't want to install anything? Open
[the book](https://adamontherun.github.io/sqlalchemy-mastery/) and click
"Launch Codespace" in any chapter's sidebar — it opens a cloud dev
environment with the exact same PostgreSQL 17 this course teaches against,
already running.

To run locally, you need [Docker](https://docs.docker.com/get-docker/) and
[uv](https://docs.astral.sh/uv/):

```sh
docker compose up -d   # starts PostgreSQL 17 on localhost:5439
uv sync                # installs Python 3.13 + all dependencies
```

The database is `postgresql://course:course@localhost:5439/course`. Port **5439**
is used on the host so it never collides with a locally installed Postgres.

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
