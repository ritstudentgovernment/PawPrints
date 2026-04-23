# session.py
from collections.abc import AsyncIterator
import contextlib
import logging

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import Config


class DataBaseSessionController:
    """
    Manage the application's async SQLAlchemy engine and session factory.

    Parameters
    ----------
    host : str
        Database URL (e.g., ``postgresql+asyncpg://user:pass@host/db``).
    engine_kwargs : dict, optional
        Additional keyword arguments forwarded to ``create_async_engine``.
        Common options include ``echo`` and ``pool_size``.

    Attributes
    ----------
    _engine : sqlalchemy.ext.asyncio.AsyncEngine or None
        The underlying async engine; ``None`` if closed.
    _sessionmaker : sqlalchemy.ext.asyncio.async_sessionmaker or None
        Factory for creating ``AsyncSession`` instances; ``None`` if closed.
    """

    def __init__(self, host: str, engine_kwargs: dict[str, object] | None = None) -> None:
        self.logger = logging.getLogger("pawprints.main")
        if engine_kwargs is None:
            engine_kwargs = {}
        self._engine = create_async_engine(host, **engine_kwargs)
        # expire_on_commit=False is a common FastAPI pattern to keep attributes accessible post-commit
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            autocommit=False,
            class_=AsyncSession,
        )

    async def close(self) -> None:
        """
        Dispose the engine and invalidate the session factory.

        Notes
        -----
        Safe to call multiple times. When already closed, logs a warning.
        """
        if self._engine is None:
            self.logger.warning(
                "DataBaseSessionController.close() called but engine is already closed"
            )
            return
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        """
        Yield a raw asynchronous connection wrapped in a transaction.

        Yields
        ------
        AsyncConnection
            An active connection with a begun transaction.

        Raises
        ------
        Exception
            Re-raises any exception after rolling back the transaction.

        Notes
        -----
        On exception, the transaction is rolled back. On success, the transaction
        is committed when the ``with`` block exits.
        """
        if self._engine is None:
            raise RuntimeError("DataBaseSessionController is not initialized (engine is closed)")

        async with self._engine.begin() as conn:
            try:
                yield conn
            except Exception:
                await conn.rollback()
                raise
            else:
                # In SQLAlchemy 2.x, begin() context commits automatically on normal exit.
                # The explicit commit here is conservative; remove if undesired.
                await conn.commit()

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """
        Yield an ``AsyncSession`` following a unit-of-work pattern.

        Yields
        ------
        AsyncSession
            An asynchronous session bound to the configured engine.

        Raises
        ------
        Exception
            Re-raises any exception after rolling back.

        Notes
        -----
        Behavior:
        - On successful exit, commits the transaction.
        - On exception inside the context, rolls back and re-raises.
        - Always closes the session.

        If you prefer explicit commits in route handlers, you can switch to:
        - Do not commit on success (remove the commit in the ``else`` block).
        """
        if self._sessionmaker is None:
            raise RuntimeError(
                "DataBaseSessionController is not initialized (sessionmaker is closed)"
            )

        session: AsyncSession = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        else:
            # Commit on success; comment this out to enforce explicit commits by callers.
            await session.commit()
        finally:
            await session.close()


# Instantiate the controller using the app's configuration
config = Config()
DATABASE_URL = config.SQLALCHEMY_DATABASE_URI
sessioncontroller = DataBaseSessionController(DATABASE_URL)


async def get_async_db_session() -> AsyncIterator[AsyncSession]:
    """
    FastAPI dependency that yields an ``AsyncSession``.

    Yields
    ------
    AsyncSession
        A database session within a unit-of-work context.
    """
    async with sessioncontroller.session() as session:
        yield session
