"""Chapter 10 challenge — build the transactional test harness.

Make `uv run pytest challenges/ch10` pass.

You're implementing the machinery from examples/ch10/conftest.py as a
reusable class. The meta-tests will use your harness the way a test suite
would — including committing inside a "test" — and then verify the database
came out untouched.
"""

from sqlalchemy import Engine
from sqlalchemy.orm import Session


class TransactionalTestHarness:
    """Wraps one test's database access in a disposable transaction.

    Usage (what the tests do):

        harness = TransactionalTestHarness(engine)
        session = harness.start()   # open connection + OUTER transaction,
                                    # return a Session that joins it via
                                    # join_transaction_mode="create_savepoint"
        ... test body: session.add(...), session.commit(), ...
        harness.stop()              # close session, ROLL BACK the outer
                                    # transaction, close the connection

    After stop(), nothing the session did — commits included — may be
    visible to any other connection.
    """

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def start(self) -> Session:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError
