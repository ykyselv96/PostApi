from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from core.config.system_config import settings


engine = create_async_engine(settings.DATABASE_URI)


async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:  # noqa: B008
    """Generate a new database session for asynchronous operations.

    This function provides a context manager that yields an
    `AsyncSession` instance. It ensures that the session is
    properly closed after use.

    Yields:
        AsyncSession: An asynchronous database session for executing queries.
    Usage:
        async with get_session() as session:
            # Perform database operations using the session
    """
    async with async_session() as session:
        await session.connection()
        yield session
