"""Chapter 10 reference solution."""

from sqlalchemy import Engine
from sqlalchemy.orm import Session


class TransactionalTestHarness:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self._connection = None
        self._transaction = None
        self._session = None

    def start(self) -> Session:
        self._connection = self.engine.connect()
        self._transaction = self._connection.begin()
        self._session = Session(
            bind=self._connection,
            join_transaction_mode="create_savepoint",
        )
        return self._session

    def stop(self) -> None:
        self._session.close()
        self._transaction.rollback()
        self._connection.close()
