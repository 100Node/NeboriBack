from collections.abc import Sequence
import uuid
from typing import Any, Protocol
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.repository import BaseRepository
from app.modules.videos.models import Video, VideoHlsUrl
from app.modules.videos.schemas import StreamItem


class IVideoRepository(Protocol):
    async def get(self, id: uuid.UUID) -> Video | None: ...
    async def create(self, obj_in: dict, flush: bool = True, commit: bool = True) -> Video: ...
    async def update(self, db_obj: Video, obj_in: dict, flush: bool = True, commit: bool = True) -> Video: ...
    async def delete(self, db_obj: Video, commit: bool = True) -> None: ...
    async def get_multi(self, limit: int = 100, offset: int = 0) -> Sequence[Video]: ...
    async def add_hls_urls(self, video_id: uuid.UUID, streams: list[StreamItem]) -> None: ...
    async def commit(self) -> None: ...


class VideoRepository(BaseRepository[Video]):
    def __init__(self, db: AsyncSession):
        super().__init__(Video, db)

    async def get(self, id: uuid.UUID) -> Video | None:
        stmt = select(Video).where(Video.id == id).options(selectinload(Video.hls_urls))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(self, limit: int = 100, offset: int = 0) -> Sequence[Video]:
        stmt = select(Video).options(selectinload(Video.hls_urls)).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def add_hls_urls(self, video_id: uuid.UUID, streams: list[StreamItem]) -> None:
        for stream in streams:
            db_url = VideoHlsUrl(
                video_id=video_id,
                resolution=stream.resolution,
                url=stream.url
            )
            self.db.add(db_url)

    async def commit(self) -> None:
        await self.db.commit()