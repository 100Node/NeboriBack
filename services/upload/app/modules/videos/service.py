import uuid
import logging
from fastapi import UploadFile

from app.modules.videos.repository import IVideoRepository
from app.modules.videos.enums import VideoStatusEnum
from app.services.storage import S3Service
from app.core.config import settings

logger = logging.getLogger(__name__)


class VideoUploadService:
    def __init__(self, repo: IVideoRepository, s3_service: S3Service):
        self.repo = repo
        self.s3_service = s3_service

    async def process_upload(self, title: str, video_id: uuid.UUID, user_id: int, file: UploadFile):
        content_type = file.content_type or "application/octet-stream"
        if not content_type.startswith("video/"):
            raise ValueError("Uploaded file must be a video.")

        filename = file.filename or "unknown.mp4"
        file_extension = filename.split(".")[-1] if "." in filename else "mp4"
        s3_object_name = f"{user_id}/{video_id}/{uuid.uuid4()}.{file_extension}"

        upload_record = await self.repo.create({
            "video_id": video_id,
            "user_id": user_id,
            "title": title,
            "filename": filename,
            "s3_path": s3_object_name,
            "status": VideoStatusEnum.PENDING,
        }, commit=False)

        try:
            await self.s3_service.ensure_bucket_exists()
            await self.s3_service.upload_video(
                file_obj=file.file,
                object_name=s3_object_name,
                content_type=content_type,
            )

            await self.repo.update(upload_record, {"status": VideoStatusEnum.PROCESSING}, commit=False)

            from app.main import broker

            # Повідомляємо metadata що upload стартував
            await broker.publish(
                message={
                    "payload": {
                        "video_id": str(video_id),
                    }
                },
                queue="video.upload.started",  # ← виправлено: було "video.upload.events"
            )

            # Повідомляємо transcoding щоб почав обробку
            await broker.publish(
                message={
                    "payload": {
                        "video_id": str(video_id),
                        "user_id": user_id,
                        "s3_bucket": settings.S3_BUCKET_NAME,
                        "s3_path": s3_object_name,
                    }
                },
                queue="video.upload.events",
            )

            await self.repo.update(upload_record, {"status": VideoStatusEnum.READY}, commit=False)
            await self.repo.commit()
            return upload_record

        except Exception as e:
            await self.repo.rollback()
            logger.error(f"Upload failed: {e}")
            try:
                await self.repo.create({
                    "video_id": video_id,
                    "user_id": user_id,
                    "title": title,
                    "filename": filename,
                    "s3_path": s3_object_name,
                    "status": VideoStatusEnum.FAILED,
                })
            except Exception:
                pass
            raise RuntimeError(f"Failed to process upload: {str(e)}")

    async def delete_upload(self, video_id: uuid.UUID, user_id: int) -> None:
        upload = await self.repo.get_by_video_id(video_id)
        if not upload:
            raise ValueError(f"Upload record for video {video_id} not found")
        if upload.user_id != user_id:
            raise PermissionError("You are not allowed to delete this video")

        await self.s3_service.delete_video(upload.s3_path)
        await self.repo.delete(upload, commit=True)

        from app.main import broker
        await broker.publish(
            message={
                "payload": {
                    "video_id": str(video_id),
                    "user_id": user_id,
                }
            },
            queue="video.deleted",
        )
        logger.info(f"Video {video_id} deleted by user {user_id}")

    async def delete_raw_file(self, video_id: uuid.UUID) -> None:
        """Видаляє лише raw файл з MinIO після успішного транскодингу. Запис в БД лишається."""
        upload = await self.repo.get_by_video_id(video_id)
        if not upload:
            logger.warning(f"Upload record for video {video_id} not found, skipping raw delete")
            return

        if not upload.s3_path:
            return

        try:
            await self.s3_service.delete_video(upload.s3_path)
            await self.repo.update(upload, {"s3_path": ""}, commit=True)
            logger.info(f"Raw file deleted for video {video_id} after successful transcoding")
        except Exception as e:
            logger.error(f"Failed to delete raw file for {video_id}: {e}")