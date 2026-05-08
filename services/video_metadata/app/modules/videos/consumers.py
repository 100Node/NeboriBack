from faststream import Depends
from faststream.rabbit import RabbitRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.modules.videos.schemas import (
    VideoProcessedEvent,
    VideoFailedEvent,
    VideoDeletedEvent,
    VideoUploadStartedEvent,
    VideoTranscodingStartedEvent,
)
from app.modules.videos.service import VideoMetadataService
from app.modules.videos.repository import VideoRepository


router = RabbitRouter()


async def get_video_service() -> VideoMetadataService:
    async with AsyncSessionLocal() as session:
        repo = VideoRepository(session)
        yield VideoMetadataService(repository=repo)


@router.subscriber("video.upload.started")
async def handle_upload_started(
    event: VideoUploadStartedEvent,
    service: VideoMetadataService = Depends(get_video_service),
):
    await service.set_status_uploading(event.payload.video_id)


@router.subscriber("video.transcoding.started")
async def handle_transcoding_started(
    event: VideoTranscodingStartedEvent,
    service: VideoMetadataService = Depends(get_video_service),
):
    await service.set_status_transcoding(event.payload.video_id)


@router.subscriber("video.processing.done")
async def handle_video_processed(
    event: VideoProcessedEvent,
    service: VideoMetadataService = Depends(get_video_service),
):
    await service.publish_video(
        video_id=event.payload.video_id,
        streams=event.payload.streams,
        duration=event.payload.duration,
    )


@router.subscriber("video.processing.failed")
async def handle_video_failed(
    event: VideoFailedEvent,
    service: VideoMetadataService = Depends(get_video_service),
):
    await service.fail_video(
        video_id=event.payload.video_id,
        error_msg=event.payload.error_message,
    )


@router.subscriber("video.deleted")
async def handle_video_deleted(
    event: VideoDeletedEvent,
    service: VideoMetadataService = Depends(get_video_service),
):
    await service.delete_video(event.payload.video_id)