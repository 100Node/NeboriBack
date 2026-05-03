from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.repository import BaseRepository
from app.modules.videos.models import VideoUpload

class IVideoRepository(Protocol):
    async def create(self, obj_in: dict, flush: bool = True) -> VideoUpload: ...
    async def update(self, db_obj: VideoUpload, obj_in: dict, flush: bool = True) -> VideoUpload: ...

class VideoUploadRepository(BaseRepository[VideoUpload]):
    def __init__(self, db: AsyncSession):
        super().__init__(VideoUpload, db)