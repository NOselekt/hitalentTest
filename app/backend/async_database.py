from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from config import settings

"""Creating an async engine for the database"""
engine = create_async_engine(settings.async_database_url, echo=settings.db_echo)

"""Creating an async session with the engine"""
local_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """Generates an async session for the database"""
    async with local_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
