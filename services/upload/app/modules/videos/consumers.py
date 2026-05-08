import uuid
import logging
from faststream import Depends
from faststream.rabbit import RabbitRouter
from pydantic import BaseModel, ConfigDict

from app.db.session import AsyncSessionLocal
from app.modules.videos.repository import VideoUploadRepository
from app.services.storage import S3Service
from app.modules.videos.service import VideoUploadService

logger = logging.getLogger(__name__)
router = RabbitRouter()


# --- Схеми подій (тільки те що нам треба) ---

class VideoProcessedPayload(BaseModel):
    video_id: uuid.UUID

class VideoProcessedEvent(BaseModel):
    model_config = ConfigDict(extra='ignore')
    payload: VideoProcessedPayload

class VideoDeletedPayload(BaseModel):
    video_id: uuid.UUID
    user_id: int

class VideoDeletedEvent(BaseModel):
    model_config = ConfigDict(extra='ignore')
    payload: VideoDeletedPayload


# --- FastStream-сумісна dependency ---

async def get_upload_service() -> VideoUploadService:
    async with AsyncSessionLocal() as session:
        repo = VideoUploadRepository(session)
        yield VideoUploadService(repo=repo, s3_service=S3Service())


# --- Consumers ---

@router.subscriber("video.processing.done")
async def handle_transcoding_done(
    event: VideoProcessedEvent,
    service: VideoUploadService = Depends(get_upload_service),
) -> None:
    """Після успішного транскодингу — видаляємо raw файл, запис лишається."""
    await service.delete_raw_file(video_id=event.payload.video_id)


@router.subscriber("video.deleted")
async def handle_video_deleted(
    event: VideoDeletedEvent,
    service: VideoUploadService = Depends(get_upload_service),
) -> None:
    """Якщо відео видалено з metadata — прибираємо raw файл якщо ще лишився."""
    upload = await service.repo.get_by_video_id(event.payload.video_id)
    if upload and upload.s3_path:
        try:
            await service.s3_service.delete_video(upload.s3_path)
            await service.repo.update(upload, {"s3_path": ""}, commit=True)
            logger.info(f"Raw file cleaned up for deleted video {event.payload.video_id}")
        except Exception as e:
            logger.error(f"Failed to clean raw file for {event.payload.video_id}: {e}")