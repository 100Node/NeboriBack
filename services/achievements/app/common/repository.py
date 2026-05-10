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

    async def create(self, obj_in: dict, flush: bool = True, commit: bool = True) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        if commit:
            await self.db.commit()
            await self.db.refresh(db_obj)
        elif flush:
            await self.db.flush()
            await self.db.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: ModelType, obj_in: dict, flush: bool = True, commit: bool = True) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        if commit:
            await self.db.commit()
            await self.db.refresh(db_obj)
        elif flush:
            await self.db.flush()
            await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, db_obj: ModelType, commit: bool = True) -> None:
        await self.db.delete(db_obj)
        if commit:
            await self.db.commit()

    async def get_multi(self, limit: int = 100, offset: int = 0):
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()