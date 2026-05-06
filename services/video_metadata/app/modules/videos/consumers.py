from faststream import Depends
from faststream.rabbit import RabbitRouter

from app.modules.videos.schemas import (
    VideoProcessedEvent,
    VideoFailedEvent,
    VideoDeletedEvent
)
from app.modules.videos.service import VideoMetadataService
from app.modules.videos.dependencies import get_video_service


router = RabbitRouter()


@router.subscriber("video.processing.done")
async def handle_video_processed(
    event: VideoProcessedEvent,
    service: VideoMetadataService = Depends(get_video_service)
):
    await service.publish_video(
        video_id=event.payload.video_id,
        hls_url=event.payload.hls_url,
        duration=event.payload.duration
    )


@router.subscriber("video.processing.failed")
async def handle_video_failed(
    event: VideoFailedEvent,
    service: VideoMetadataService = Depends(get_video_service)
):
    await service.fail_video(
        video_id=event.payload.video_id,
        error_msg=event.payload.error_message
    )


@router.subscriber("video.deleted")
async def handle_video_deleted(
    event: VideoDeletedEvent,
    service: VideoMetadataService = Depends(get_video_service)
):
    await service.delete_video(
        video_id=event.payload.video_id
    )
