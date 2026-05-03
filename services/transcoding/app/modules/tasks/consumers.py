import os
import shutil
import asyncio
import logging
from faststream.rabbit import RabbitRouter

from app.modules.tasks.schemas import VideoUploadedEvent, VideoProcessedEvent, VideoProcessedPayload
from app.services.storage import S3TranscodeService
from app.services.transcoder import FFmpegService

logger = logging.getLogger(__name__)
router = RabbitRouter()

s3_service = S3TranscodeService()
transcoder = FFmpegService()

TEMP_WORK_DIR = "/tmp/nebori_processing"
PROCESSED_BUCKET = "processed-videos" # Можна винести в config.py

@router.subscriber("video.upload.events")
@router.publisher("video.processing.done") # <--- FastStream сам відправить return у цю чергу!
async def process_video_upload(event: VideoUploadedEvent) -> VideoProcessedEvent:
    video_id = event.payload.video_id
    user_id = event.payload.user_id
    logger.info(f"Started processing pipeline for video: {video_id}")
    
    video_work_dir = os.path.join(TEMP_WORK_DIR, str(video_id))
    local_raw_path = os.path.join(video_work_dir, "raw.mp4")
    
    out_audio = os.path.join(video_work_dir, "audio.mp3")
    out_1080p = os.path.join(video_work_dir, "1080p.mp4")
    out_720p = os.path.join(video_work_dir, "720p.mp4")
    
    try:
        # 1. Завантажуємо
        await s3_service.download_video(
            bucket_name=event.payload.s3_bucket,
            object_name=event.payload.s3_path,
            local_file_path=local_raw_path
        )
        
        # 2. Транскодуємо
        await asyncio.gather(
            transcoder.extract_audio(local_raw_path, out_audio),
            transcoder.transcode_video(local_raw_path, out_1080p, "1920x1080"),
            transcoder.transcode_video(local_raw_path, out_720p, "1280x720")
        )
        
        # 3. Завантажуємо ГОТОВІ файли назад в S3 (паралельно!)
        s3_base_path = f"{user_id}/{video_id}"
        
        # Використовуємо gather для пришвидшення мережевих запитів
        await asyncio.gather(
            s3_service.upload_file(PROCESSED_BUCKET, f"{s3_base_path}/audio.mp3", out_audio, "audio/mpeg"),
            s3_service.upload_file(PROCESSED_BUCKET, f"{s3_base_path}/1080p.mp4", out_1080p, "video/mp4"),
            s3_service.upload_file(PROCESSED_BUCKET, f"{s3_base_path}/720p.mp4", out_720p, "video/mp4")
        )
        
        logger.info(f"Pipeline successfully completed for {video_id}")
        
        # 4. Повертаємо івент (FastStream сам відправить його в RabbitMQ)
        return VideoProcessedEvent(
            payload=VideoProcessedPayload(
                video_id=video_id,
                audio_path=f"{s3_base_path}/audio.mp3",
                video_1080p_path=f"{s3_base_path}/1080p.mp4",
                video_720p_path=f"{s3_base_path}/720p.mp4"
            )
        )
        
    except Exception as e:
        logger.error(f"Pipeline failed for video {video_id}: {e}")
        raise
        
    finally:
        # 5. CLEANUP: Цей блок виконається ЗАВЖДИ в кінці
        if os.path.exists(video_work_dir):
            shutil.rmtree(video_work_dir)
            logger.info(f"Cleaned up temporary directory: {video_work_dir}")