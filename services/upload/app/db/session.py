from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings


DATABASE_URL_ASYNC = settings.DATABASE_URL_ASYNC
DATABASE_URL_SYNC = settings.DATABASE_URL_SYNC

engine = create_async_engine(
    DATABASE_URL_ASYNC,
    echo=False,
    poolclass=NullPool,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session 
            
        except Exception:
            await session.rollback() 
            raise 
        finally:
            await session.close()


engine_sync = create_engine(
    DATABASE_URL_SYNC,
    echo=False,
    pool_pre_ping=True,
)

SessionLocalSync = sessionmaker(
    bind=engine_sync,
    autocommit=False,
    autoflush=False,
)
