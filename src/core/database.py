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


#################
# TRUNCARTE SCRIPT


# DO $$
# DECLARE
#   tbls text := '';
#   r record;
# BEGIN
#   FOR r IN
#     SELECT quote_ident(n.nspname) || '.' || quote_ident(c.relname) AS full_table
#     FROM pg_class c
#     JOIN pg_namespace n ON n.oid = c.relnamespace
#     WHERE c.relkind = 'r'
#       AND n.nspname = 'public'
#       AND NOT (quote_ident(n.nspname) || '.' || quote_ident(c.relname)) IN (
#         'public.alembic_version', 'public.permissions'
#       )
#   LOOP
#     tbls := tbls || CASE WHEN tbls = '' THEN '' ELSE ', ' END || r.full_table;
#   END LOOP;

#   IF tbls = '' THEN
#     RAISE NOTICE 'No tables to truncate in public (all excluded).';
#     RETURN;
#   END IF;

#   EXECUTE 'TRUNCATE TABLE ' || tbls || ' RESTART IDENTITY CASCADE;';
#   RAISE NOTICE 'Truncated tables: %', tbls;
# END;
# $$ LANGUAGE plpgsql;

#############################