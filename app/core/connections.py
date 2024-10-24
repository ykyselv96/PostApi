from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config.system_config import settings


engine = create_async_engine(settings.DATABASE_URI)


async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:  # noqa: B008
    async with async_session() as session:
        await session.connection()
        yield session
