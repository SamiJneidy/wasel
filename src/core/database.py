from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from src.core.config import settings

# Async database URL
# postgresql+asyncpg://username:password@host/dbname
engine = create_async_engine(
    settings.SQLALCHEMY_URL,
    echo=False,
    future=True
)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    async with async_session() as session:
        yield session
