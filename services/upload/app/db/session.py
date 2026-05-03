from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings


DATABASE_URL_ASYNC = settings.DATABASE_URL_ASYNC

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

