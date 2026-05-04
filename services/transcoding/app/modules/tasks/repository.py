from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.repository import BaseRepository
from app.modules.tasks.models import ProcessingTask

class IProcessingTaskRepository(Protocol):
    async def create(self, obj_in: dict, flush: bool = True) -> ProcessingTask: ...
    async def update(self, db_obj: ProcessingTask, obj_in: dict, flush: bool = True) -> ProcessingTask: ...

class ProcessingTaskRepository(BaseRepository[ProcessingTask]):
    def __init__(self, db: AsyncSession):
        super().__init__(ProcessingTask, db)