from collections.abc import Sequence
import uuid
from typing import Any, Protocol
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.repository import BaseRepository
from app.modules.videos.models import Video, VideoStatus


class IVideoRepository(Protocol):
    async def get(self, id: uuid.UUID) -> Video | None: ...
    async def create(self, obj_in: dict, flush: bool = True) -> Video: ...
    async def update(self, db_obj: Video, obj_in: dict, flush: bool = True) -> Video: ...
    
    async def get_multi(self, limit: int = 100, offset: int = 0) -> Sequence[Video]: ...
    
    async def update_fields(self, video_id: uuid.UUID, **kwargs: Any) -> None: ...


class VideoRepository(BaseRepository[Video]):
    def __init__(self, db: AsyncSession):
        super().__init__(Video, db)

    async def update_fields(self, video_id: uuid.UUID, **kwargs: Any) -> None:
        if not kwargs:
            return
        stmt = (
            update(Video)
            .where(Video.id == video_id)
            .values(**kwargs)
        )
        await self.db.execute(stmt)
