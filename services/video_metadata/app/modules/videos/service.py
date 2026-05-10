import uuid
import logging

from app.modules.videos.repository import IVideoRepository
from app.modules.videos.models import Video
from app.modules.videos.enums import VideoStatusEnum
from app.modules.videos.schemas import VideoBase, VideoUpdate, StreamItem

logger = logging.getLogger(__name__)


class VideoMetadataService:
    def __init__(self, repository: IVideoRepository):
        self.repository = repository

    async def create_video(self, data: VideoBase, user_id: int) -> Video:
        data_to_create = data.model_dump()
        data_to_create["user_id"] = user_id
        data_to_create["status"] = VideoStatusEnum.QUEUED  # ← дефолт

        video = await self.repository.create(data_to_create, commit=True)
        fresh_video = await self.repository.get(video.id)
        if fresh_video is None:
            raise ValueError("Failed to retrieve created video metadata")
        return fresh_video

    async def set_status_uploading(self, video_id: uuid.UUID) -> None:
        video = await self.repository.get(video_id)
        if video:
            await self.repository.update(video, {"status": VideoStatusEnum.UPLOADING}, commit=True)
            logger.info(f"Video {video_id} → UPLOADING")

    async def set_status_transcoding(self, video_id: uuid.UUID) -> None:
        video = await self.repository.get(video_id)
        if video:
            await self.repository.update(video, {"status": VideoStatusEnum.TRANSCODING}, commit=True)
            logger.info(f"Video {video_id} → TRANSCODING")

    async def publish_video(self, video_id: uuid.UUID, streams: list[StreamItem], duration: int | None):
        video = await self.repository.get(video_id)
        if not video:
            logger.error(f"Video {video_id} not found")
            return

        await self.repository.update(video, {
            "status": VideoStatusEnum.PUBLISHED,
            "duration": duration,
        }, commit=False)
        await self.repository.add_hls_urls(video_id, streams)
        await self.repository.commit()
        logger.info(f"Video {video_id} → PUBLISHED")

    async def update_metadata(self, video_id: uuid.UUID, data: VideoUpdate) -> Video:
        video = await self.repository.get(video_id)
        if not video:
            raise ValueError(f"Video {video_id} not found")

        update_data = data.model_dump(exclude_unset=True)
        await self.repository.update(video, update_data, commit=True)

        fresh_video = await self.repository.get(video_id)
        if fresh_video is None:
            raise ValueError("Failed to retrieve updated video metadata")
        return fresh_video

    async def get_video(self, video_id: uuid.UUID) -> Video | None:
        return await self.repository.get(video_id)

    async def list_videos(self, limit: int = 20, offset: int = 0):
        return await self.repository.get_multi(limit=limit, offset=offset)

    async def fail_video(self, video_id: uuid.UUID, error_msg: str):
        video = await self.repository.get(video_id)
        if video:
            await self.repository.update(video, {"status": VideoStatusEnum.ERROR}, commit=True)
            logger.info(f"Video {video_id} → ERROR: {error_msg}")

    async def delete_video(self, video_id: uuid.UUID):
        video = await self.repository.get(video_id)
        if video:
            await self.repository.delete(video, commit=True)
            logger.info(f"Video {video_id} deleted")