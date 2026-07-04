# Research notes & bibliography

Distilled findings from official docs and community reports (July 2026) that shaped
this course. Kept in the repo as the course bibliography.

## Version landscape

- **SQLAlchemy 2.0.51** — current stable (June 2026). The course targets this.
- **SQLAlchemy 2.1.0b3** — beta. Key changes worth "2.1 watch" sidebars:
  - `greenlet` becomes an optional dependency: install `sqlalchemy[asyncio]` for async.
  - Python floor raised to 3.10.
  - Typing: `Select[Tuple[int, str]]` becomes `Select[int, str]` via PEP 646 `Unpack`;
    no more `Row._t` workaround. Mypy ≥ 1.7 required for typed results.
  - ORM row fetching internally uses plain tuples (perf).
  - Dataclass mapping: defaults via descriptors, new `DONT_SET` constant.
- Sources: [What's New in 2.1](https://docs.sqlalchemy.org/en/21/changelog/migration_21.html),
  [2.1.0b1 announcement](https://www.sqlalchemy.org/blog/2026/01/21/sqlalchemy-2.1.0b1-released/)

## Connection pooling (ch02)

Source: [Pooling docs](https://docs.sqlalchemy.org/en/20/core/pooling.html)

- Defaults: `QueuePool`, `pool_size=5`, `max_overflow=10`, `pool_timeout=30`,
  `pool_recycle=-1` (off), `pool_pre_ping=False`, `reset_on_return="rollback"`.
- Pool exhaustion math: 5 + 10 = 15 concurrent checkouts; the 16th waits 30 s then
  raises `TimeoutError: QueuePool limit of size 5 overflow 10 reached`. Almost always
  a symptom of leaked connections (checked out, never closed) rather than real load.
- `pool_pre_ping=True` = pessimistic disconnect handling ("SELECT 1" on checkout);
  optimistic handling relies on invalidate-on-error. `pool_recycle=3600` for servers
  (MySQL famously; also firewalls/LBs) that kill idle connections.
- Forking (gunicorn prefork, `multiprocessing`): pools must NOT cross process
  boundaries — call `engine.dispose(close=False)` in the child after fork.
- **pgbouncer**: application-side QueuePool + transaction-mode pgbouncer stack two
  pools and misbehave; recommended: `NullPool` and let pgbouncer own pooling,
  keep per-process pools small, or skip pgbouncer entirely at moderate scale.
- Asyncio: `QueuePool` uses a `threading.Lock` → incompatible; async engines
  automatically get `AsyncAdaptedQueuePool`. `NullPool`/`StaticPool` are async-safe.

## Session (ch05)

Source: [Session basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)

- Unit of work: Session batches pending changes, flushes before queries/commit.
- Identity map: one Python object per row per session; it is NOT a query cache —
  only `session.get(pk)` can skip SQL.
- Object states: transient → pending (`add()`) → persistent (flush) → detached (close).
- `commit()` = flush + COMMIT; autoflush runs before queries. Flush ≠ commit.
- `expire_on_commit=True` (default): all attributes expire after commit, next access
  reloads. Great for strict freshness, terrible for async (see ch08) and for
  access-after-response patterns.
- Docs' explicit guidance: "keep the lifecycle of the session separate and external"
  from data-access code; session-per-operation, passed in as a parameter. The docs
  literally mark embedded session management as "the wrong way to do it".
- Not thread-safe; one Session per thread / one AsyncSession per asyncio task.
- `sessionmaker` created once at module scope as a factory.

## Relationship loading (ch07)

Source: [Relationship loading techniques](https://docs.sqlalchemy.org/en/20/orm/queryguide/relationships.html)

- Lazy (`select`) is the default → the N+1 problem.
- `selectinload()` — "generally the best loading strategy": second SELECT with IN
  on parent PKs; best for collections (1:N, M:N).
- `joinedload()` — LEFT OUTER JOIN in the same statement; best for many-to-one.
  **With collections you must call `.unique()` on the Result** or SQLAlchemy raises.
- `subqueryload()` — legacy, prefer selectin.
- `raiseload()` — turns would-be lazy loads into errors; great as a discipline tool
  and in tests to flush out hidden N+1s.
- `contains_eager()` — reuse a JOIN you already wrote yourself.
- Loader options are "sticky" on instances until expired/refreshed.

## Asyncio (ch08)

Source: [Asyncio extension docs](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html),
[MissingGreenlet discussions](https://github.com/sqlalchemy/sqlalchemy/discussions/9757)

- Architecture: async API wraps the sync Core/ORM internals via greenlets. The DBAPI
  driver (asyncpg) is truly async; the ORM machinery context-switches through greenlet.
- **No implicit IO allowed.** Any attribute access that would lazy-load raises
  `MissingGreenlet: greenlet_spawn has not been called`. The #1 async gotcha.
  Triggers: lazy relationships, deferred columns, and *expired attributes after
  commit* (which is why `expire_on_commit=False` is in every async example).
- Fixes: eager load (`selectinload`), `AsyncAttrs` mixin → `await obj.awaitable_attrs.x`,
  `await session.refresh(obj, ["x"])`, or `run_sync()` as an escape hatch.
- One `AsyncSession` per task — never share across concurrent tasks.
- Engines must not hop event loops; call `await engine.dispose()` before reuse in a
  new loop (or use `NullPool`). Always `await engine.dispose()` at shutdown or GC may
  print `RuntimeError: Event loop is closed`.
- `AsyncConnection.stream()` for server-side-cursor streaming; `execute()` buffers.
- Events are registered on `engine.sync_engine` / the sync `Session` class.
- **asyncpg + pgbouncer trap**: transaction-mode pgbouncer breaks asyncpg's prepared
  statement cache → `DuplicatePreparedStatementError`. Fix: `statement_cache_size=0`
  AND `prepared_statement_cache_size=0` in `connect_args` (both!), or use NullPool /
  skip pgbouncer. ([sqlalchemy#6467](https://github.com/sqlalchemy/sqlalchemy/issues/6467),
  [asyncpg FAQ](https://magicstack.github.io/asyncpg/current/faq.html))

## Alembic (ch09)

Source: [Autogenerate docs](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)

- Autogenerate DETECTS: table add/remove; column add/remove; nullable changes;
  basic indexes + named unique constraints; basic FKs.
- Optionally detects: column type changes (`compare_type`, on by default since 1.12),
  server defaults (`compare_server_default=True`, "cannot always produce accurate results").
- CANNOT detect: renames (seen as drop+add!), anonymously named constraints,
  CHECK/PK/EXCLUDE constraints, sequences.
- Therefore: set a **naming convention** on `MetaData` from day one (ch04 covers it),
  and always review generated migrations — "autogenerate is not intended to be perfect."
- Async setup: `alembic init -t async`; env.py wraps sync `do_run_migrations` in
  `connection.run_sync()` inside `asyncio.run(run_async_migrations())`. Use
  `NullPool` for the short-lived migration engine.

## Testing (ch10)

Source: [Session transactions — joining an external transaction](https://docs.sqlalchemy.org/en/20/orm/session_transaction.html)

- Canonical rollback-per-test recipe: open a Connection + outer transaction in the
  fixture, bind the Session with `join_transaction_mode="create_savepoint"`, roll the
  outer transaction back in teardown. Test code can commit freely — commits become
  SAVEPOINT releases and everything vanishes on teardown rollback.
- pytest-asyncio `asyncio_mode = "auto"` keeps async test boilerplate down.

## FastAPI integration (ch12)

Sources: community patterns (Medium/Hashnode guides, 2025–2026), FastAPI docs

- Engine + `async_sessionmaker` created once, ideally in `lifespan`; dispose on shutdown.
- Session-per-request via a `Depends` generator that yields an `AsyncSession`.
  FastAPI caches a dependency within one request → repositories share the session.
- Commit at the end of the request handler (or in the dependency), rollback on error.
- `expire_on_commit=False` mandatory — response serialization happens after commit.
- Serialization gotcha: Pydantic touching a lazy relationship after the session is
  closed → `MissingGreenlet`/`DetachedInstanceError`. Eager-load whatever the
  response model needs.
- Measured community benchmarks report ~3–5× more req/s for async DB endpoints under
  IO-bound load (locust tests) vs sync equivalents.

## Recurring themes to weave through the book

1. Name your constraints (naming conventions) before you ever run Alembic.
2. `expire_on_commit` is behind half of all "SQLAlchemy is broken" reports.
3. Pool exhaustion is usually a leak, not load.
4. The async layer forbids implicit IO — design for explicit loading.
5. Old tutorials (Query API, `declarative_base()`, implicit autocommit) are the main
   source of confusion; recognize 1.x patterns so you can avoid them.
