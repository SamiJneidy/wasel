from typing import AsyncIterator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from src.core.config import settings

# Async database URL
# postgresql+asyncpg://username:password@host/dbname
engine = create_async_engine(
    settings.SQLALCHEMY_URL,
    echo=False,
    future=True,
    # connect_args={"statement_cache_size": 0} # connect_args are usually for sync engines
)

async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False # Ensure autocommit is off for explicit transaction management
)

Base = declarative_base()

# --- The Modified get_db Dependency ---
async def get_db() -> AsyncIterator[AsyncSession]:
    """Provides a transactional scope for the entire request."""
    async with async_session() as session:
        try:
            # *** ADDED: Start the transaction for all dependencies/routes ***
            async with session.begin(): 
                yield session
            # Transaction commits automatically here if no exceptions occurred

        except Exception:
            await session.rollback()
            raise
            
        finally:
            await session.close()
