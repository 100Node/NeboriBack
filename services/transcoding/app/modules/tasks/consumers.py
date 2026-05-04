import os
import shutil
import asyncio
import logging
from faststream.rabbit import RabbitRouter

from app.modules.tasks.schemas import VideoUploadedEvent, VideoProcessedEvent, VideoProcessedPayload
from app.services.storage import S3TranscodeService
from app.services.transcoder import FFmpegService
from app.core.config import settings

logger = logging.getLogger(__name__)
router = RabbitRouter()

s3_service = S3TranscodeService()
transcoder = FFmpegService()

TEMP_WORK_DIR = "/tmp/nebori_processing"

@router.subscriber("video.upload.events")
@router.publisher("video.processing.done")
async def process_video_upload(event: VideoUploadedEvent) -> VideoProcessedEvent:
    video_id = event.payload.video_id
    user_id = event.payload.user_id
    logger.info(f"Started processing pipeline for video: {video_id}")
    
    video_work_dir = os.path.join(TEMP_WORK_DIR, str(video_id))
    local_raw_path = os.path.join(video_work_dir, "raw.mp4")
    
    # ---------------------------------------------------------
    # НОВЕ: Шляхи для вихідних даних (тепер для відео це папки!)
    # ---------------------------------------------------------
    out_audio = os.path.join(video_work_dir, "audio.mp3")
    out_1080p_dir = os.path.join(video_work_dir, "1080p")
    out_720p_dir = os.path.join(video_work_dir, "720p")
    
    try:
        # 1. Завантажуємо
        await s3_service.download_video(
            bucket_name=event.payload.s3_bucket,
            object_name=event.payload.s3_path,
            local_file_path=local_raw_path
        )
        
        # 2. Транскодуємо
        # Замість transcode_video викликаємо новий метод transcode_to_hls
        # Він збереже купу файлів (.m3u8 та .ts) у відповідні папки
        await asyncio.gather(
            transcoder.extract_audio(local_raw_path, out_audio),
            transcoder.transcode_to_hls(local_raw_path, out_1080p_dir, "1920x1080"),
            transcoder.transcode_to_hls(local_raw_path, out_720p_dir, "1280x720")
        )
        
        # 3. Завантажуємо ГОТОВІ файли назад в S3 (паралельно!)
        s3_base_path = f"{user_id}/{video_id}"
        
        # Використовуємо upload_directory для папок з HLS
        await asyncio.gather(
            s3_service.upload_file(settings.S3_PROCESSED_BUCKET_NAME, f"{s3_base_path}/audio.mp3", out_audio, "audio/mpeg"),
            s3_service.upload_directory(out_1080p_dir, f"{s3_base_path}/1080p", settings.S3_PROCESSED_BUCKET_NAME),
            s3_service.upload_directory(out_720p_dir, f"{s3_base_path}/720p", settings.S3_PROCESSED_BUCKET_NAME)
        )
        
        logger.info(f"Pipeline successfully completed for {video_id}")
        
        # 4. Повертаємо івент (FastStream сам відправить його в RabbitMQ)
        # ЗВЕРНИ УВАГУ: Тепер ми повертаємо шляхи до файлів index.m3u8, а не до mp4!
        return VideoProcessedEvent(
            payload=VideoProcessedPayload(
                video_id=video_id,
                audio_path=f"{s3_base_path}/audio.mp3",
                video_1080p_path=f"{s3_base_path}/1080p/index.m3u8",
                video_720p_path=f"{s3_base_path}/720p/index.m3u8"
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