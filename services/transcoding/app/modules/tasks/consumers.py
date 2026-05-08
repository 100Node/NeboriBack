import os
import shutil
import asyncio
import logging
from faststream.rabbit import RabbitRouter

from app.modules.tasks.schemas import (
    VideoUploadedEvent,
    VideoProcessedEvent,
    VideoProcessedPayload,
    VideoCanceledEvent,
    VideoDeletedEvent,
    StreamItem,
)
from app.services.storage import S3TranscodeService
from app.services.transcoder import FFmpegService
from app.core.config import settings

logger = logging.getLogger(__name__)
router = RabbitRouter()

s3_service = S3TranscodeService()
transcoder = FFmpegService()

TEMP_WORK_DIR = "/tmp/nebori_processing"
ACTIVE_TASKS: dict[str, asyncio.Task] = {}


@router.subscriber("video.upload.events")
@router.publisher("video.processing.done")
async def process_video_upload(event: VideoUploadedEvent) -> VideoProcessedEvent | None:
    video_id = str(event.payload.video_id)
    user_id = str(event.payload.user_id)

    current_task = asyncio.current_task()
    if current_task:
        ACTIVE_TASKS[video_id] = current_task

    video_work_dir = os.path.join(TEMP_WORK_DIR, video_id)
    local_raw_path = os.path.join(video_work_dir, "raw.mp4")
    out_audio = os.path.join(video_work_dir, "audio.mp3")
    out_1080p_dir = os.path.join(video_work_dir, "1080p")
    out_720p_dir = os.path.join(video_work_dir, "720p")

    try:
        os.makedirs(video_work_dir, exist_ok=True)

        await s3_service.download_video(
            bucket_name=event.payload.s3_bucket,
            object_name=event.payload.s3_path,
            local_file_path=local_raw_path,
        )

        # Повідомляємо metadata що починається транскодинг
        from app.main import broker
        await broker.publish(
            message={"payload": {"video_id": str(event.payload.video_id)}},
            queue="video.transcoding.started",
        )

        await asyncio.gather(
            transcoder.extract_audio(local_raw_path, out_audio),
            transcoder.transcode_to_hls(local_raw_path, out_1080p_dir, "1920x1080"),
            transcoder.transcode_to_hls(local_raw_path, out_720p_dir, "1280x720"),
        )

        s3_base_path = f"{user_id}/{video_id}"

        await asyncio.gather(
            s3_service.upload_file(settings.S3_PROCESSED_BUCKET_NAME, f"{s3_base_path}/audio.mp3", out_audio, "audio/mpeg"),
            s3_service.upload_directory(out_1080p_dir, f"{s3_base_path}/1080p", settings.S3_PROCESSED_BUCKET_NAME),
            s3_service.upload_directory(out_720p_dir, f"{s3_base_path}/720p", settings.S3_PROCESSED_BUCKET_NAME),
        )

        logger.info(f"Pipeline successfully completed for {video_id}")

        return VideoProcessedEvent(
            payload=VideoProcessedPayload(
                video_id=event.payload.video_id,
                streams=[
                    StreamItem(resolution="audio", url=f"{s3_base_path}/audio.mp3"),
                    StreamItem(resolution="1080p", url=f"{s3_base_path}/1080p/index.m3u8"),
                    StreamItem(resolution="720p", url=f"{s3_base_path}/720p/index.m3u8"),
                ],
                duration=None,
            )
        )

    except asyncio.CancelledError:
        logger.warning(f"Pipeline for {video_id} was ABORTED")
        return None
    except Exception as e:
        logger.error(f"Pipeline failed for {video_id}: {e}")
        raise
    finally:
        ACTIVE_TASKS.pop(video_id, None)
        if os.path.exists(video_work_dir):
            shutil.rmtree(video_work_dir, ignore_errors=True)


@router.subscriber("video.deleted")
async def handle_video_deleted(event: VideoDeletedEvent) -> None:
    video_id = str(event.payload.video_id)
    prefix = f"{event.payload.user_id}/{video_id}/"
    try:
        await s3_service.delete_prefix(settings.S3_PROCESSED_BUCKET_NAME, prefix)
        logger.info(f"Deleted processed files for video {video_id}")
    except Exception as e:
        logger.error(f"Failed to delete processed files for {video_id}: {e}")