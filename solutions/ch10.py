"""Chapter 10 reference solution."""

from sqlalchemy import Connection, Engine, RootTransaction
from sqlalchemy.orm import Session


class TransactionalTestHarness:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self._connection: Connection | None = None
        self._transaction: RootTransaction | None = None
        self._session: Session | None = None

    def start(self) -> Session:
        self._connection = self.engine.connect()
        self._transaction = self._connection.begin()
        self._session = Session(
            bind=self._connection,
            join_transaction_mode="create_savepoint",
        )
        return self._session

    def stop(self) -> None:
        assert self._session is not None, "call start() before stop()"
        assert self._transaction is not None, "call start() before stop()"
        assert self._connection is not None, "call start() before stop()"
        self._session.close()
        self._transaction.rollback()
        self._connection.close()
