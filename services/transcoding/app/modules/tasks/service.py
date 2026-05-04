from typing import Awaitable, Callable
import uuid
import logging
from fastapi import UploadFile

from app.modules.tasks.repository import IProcessingTaskRepository
from app.modules.tasks.enums import TaskStatusEnum, TaskTypeEnum
from app.services.storage import S3Service

logger = logging.getLogger(__name__)

class VideoUploadService:
    def __init__(
        self, 
        repo: IProcessingTaskRepository, 
        s3_service: S3Service,
        commit_func: Callable[[], Awaitable[None]], 
        rollback_func: Callable[[], Awaitable[None]]
    ):
        self.repo = repo
        self.s3_service = s3_service
        self.commit = commit_func
        self.rollback = rollback_func

    async def process_upload(self, title: str, video_id: uuid.UUID, user_id: uuid.UUID, file: UploadFile):
        content_type = file.content_type or "application/octet-stream"
        if not content_type.startswith("video/"):
            raise ValueError("Uploaded file must be a video.")

        filename = file.filename or "unknown.mp4"
        file_extension = filename.split('.')[-1] if '.' in filename else 'mp4'
        s3_object_name = f"{user_id}/{video_id}/{uuid.uuid4()}.{file_extension}"

        try:
            # 1. Репозиторій робить свою роботу (flush)
            upload_record = await self.repo.create({
                "video_id": video_id,
                "user_id": user_id,
                "title": title,
                "filename": filename,
                "s3_path": s3_object_name,
                "status": TaskStatusEnum.PENDING
            })

            # 2. S3 робить свою роботу
            await self.s3_service.ensure_bucket_exists()
            await self.s3_service.upload_video(
                file_obj=file.file,
                object_name=s3_object_name,
                content_type=content_type
            )
            
            # 3. Репозиторій оновлює (flush)
            await self.repo.update(upload_record, {"status": TaskStatusEnum.PROCESSING})
            
            # 4. Сервіс викликає коміт
            await self.commit()
            return upload_record

        except Exception as e:
            await self.rollback()
            logger.error(f"Transaction failed for video {video_id}: {e}")
            raise RuntimeError("Failed to process upload.")