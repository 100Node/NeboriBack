import uuid
import logging
from faststream.rabbit import RabbitBroker

from app.modules.videos.repository import IVideoRepository
from app.modules.videos.models import Video, VideoStatus
from app.modules.videos.schemas import VideoCreate, VideoUpdate


logger = logging.getLogger(__name__)


class VideoMetadataService:
    def __init__(self, repository: IVideoRepository):
        self.repository = repository

    async def create_video(self, data: VideoCreate) -> Video:
        return await self.repository.create(data.model_dump())

    async def get_video(self, video_id: uuid.UUID) -> Video | None:
        return await self.repository.get(video_id)


    async def update_metadata(self, video_id: uuid.UUID, data: VideoUpdate) -> Video:
        db_obj = await self.repository.get(video_id)
        if not db_obj:
            raise ValueError("Video not found")
        
        return await self.repository.update(
            db_obj=db_obj, 
            obj_in=data.model_dump(exclude_unset=True)
        )

    async def publish_video(self, video_id: uuid.UUID, hls_url: str, duration: int | None):
        logger.info(f"Service: Publishing video {video_id}")
        await self.repository.update_fields(
            video_id=video_id,
            playlist_url=hls_url,
            duration=duration,
            status=VideoStatus.PUBLISHED
        )

    async def fail_video(self, video_id: uuid.UUID, error_msg: str):
        logger.warning(
            f"Service: Marking video {video_id} as failed. Reason: {error_msg}")
        await self.repository.update_fields(
            video_id=video_id,
            status=VideoStatus.ERROR
        )

    async def delete_video(self, video_id: uuid.UUID):
        logger.info(f"Service: Soft-deleting video {video_id}")
        await self.repository.update_fields(
            video_id=video_id,
            status=VideoStatus.DELETED
        )

    async def cancel_video(self, video_id: uuid.UUID, broker: RabbitBroker):
        logger.info(f"Canceling video {video_id}")
        
        await self.repository.update_fields(
            video_id=video_id, 
            status=VideoStatus.CANCELED
        )
        
        await broker.publish(
            message={"payload": {"video_id": str(video_id)}},
            queue="video.canceled.events"
        )
    
    async def list_videos(self, limit: int = 20, offset: int = 0):
        return await self.repository.get_multi(limit=limit, offset=offset)