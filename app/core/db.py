from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings  # Предполагаем, что тут лежит DATABASE_URL

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для FastAPI. 
    Гарантирует закрытие сессии после завершения обработки запроса.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()