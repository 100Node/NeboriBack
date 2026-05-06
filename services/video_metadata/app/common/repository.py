from typing import Generic, TypeVar, Type, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, id: Any) -> ModelType | None:
        return await self.db.get(self.model, id)

    async def create(self, obj_in: dict, flush: bool = True) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        if flush:
            await self.db.flush()
            await self.db.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: ModelType, obj_in: dict, flush: bool = True) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        if flush:
            await self.db.flush()
            await self.db.refresh(db_obj)
        return db_obj

    async def get_multi(self, limit: int = 100, offset: int = 0):
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()