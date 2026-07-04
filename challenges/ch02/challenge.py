"""Chapter 2 challenge — engines, transactions, and money.

Make `uv run pytest challenges/ch02` pass.

You're building the two things every backend eventually needs: an engine
configured for production, and a money transfer that can never half-happen.
"""

from sqlalchemy import Engine, text


def make_production_engine(url: str) -> Engine:
    """Create an engine configured for a long-running service:

    * 10 persistent connections, up to 5 more under burst load
    * connections tested with a ping before every checkout
    * connections retired after 30 minutes (1800s), pre-empting
      firewalls and load balancers that kill idle TCP
    """
    raise NotImplementedError


def transfer(engine: Engine, from_account: str, to_account: str, amount: int) -> None:
    """Move `amount` cents between accounts in the `ch02_accounts` table
    (columns: name text primary key, balance_cents int with a CHECK >= 0).

    Requirements:
      * Both UPDATEs happen in ONE transaction: if the debit violates the
        CHECK constraint (insufficient funds), the credit must not survive.
      * Let the resulting IntegrityError propagate to the caller.
      * Hint: engine.begin() gives you exactly these semantics for free.
    """
    raise NotImplementedError


def account_balance(engine: Engine, name: str) -> int:
    """Return the balance of `name` in cents."""
    raise NotImplementedError
