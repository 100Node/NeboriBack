from typing import Protocol, Any
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.common.repository import BaseRepository
from app.modules.videos.models import VideoUpload


class IVideoRepository(Protocol):
    async def get_by_video_id(self, video_id: uuid.UUID) -> VideoUpload | None: ...
    async def create(self, obj_in: dict, flush: bool = True, commit: bool = True) -> VideoUpload: ...
    async def update(self, db_obj: VideoUpload, obj_in: dict, flush: bool = True, commit: bool = True) -> VideoUpload: ...
    async def delete(self, db_obj: VideoUpload, commit: bool = True) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...


class VideoUploadRepository(BaseRepository[VideoUpload]):
    def __init__(self, db: AsyncSession):
        super().__init__(VideoUpload, db)

    async def get_by_video_id(self, video_id: uuid.UUID) -> VideoUpload | None:
        stmt = select(VideoUpload).where(VideoUpload.video_id == video_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def commit(self) -> None:
        await self.db.commit()

    async def rollback(self) -> None:
        await self.db.rollback()