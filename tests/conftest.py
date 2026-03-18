import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.base import Base
from app.integrations.bank import BankClient

@pytest_asyncio.fixture
async def db_session():
    # Используем SQLite в памяти для тестов
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        yield session
    await engine.dispose()

@pytest.fixture
def mock_bank_client(mocker):
    # Используем pytest-mock для подмены ответов банка
    return mocker.Mock(spec=BankClient)