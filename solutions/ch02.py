"""Chapter 2 reference solution."""

from sqlalchemy import Engine, create_engine, text


def make_production_engine(url: str) -> Engine:
    return create_engine(
        url,
        pool_size=10,
        max_overflow=5,
        pool_pre_ping=True,
        pool_recycle=1800,
    )


def transfer(engine: Engine, from_account: str, to_account: str, amount: int) -> None:
    with engine.begin() as conn:  # one transaction; rollback on any exception
        conn.execute(
            text(
                "UPDATE ch02_accounts SET balance_cents = balance_cents + :amt "
                "WHERE name = :name"
            ),
            {"amt": amount, "name": to_account},
        )
        conn.execute(
            text(
                "UPDATE ch02_accounts SET balance_cents = balance_cents - :amt "
                "WHERE name = :name"
            ),
            {"amt": amount, "name": from_account},
        )


def account_balance(engine: Engine, name: str) -> int:
    with engine.connect() as conn:
        return conn.execute(
            text("SELECT balance_cents FROM ch02_accounts WHERE name = :name"),
            {"name": name},
        ).scalar_one()
