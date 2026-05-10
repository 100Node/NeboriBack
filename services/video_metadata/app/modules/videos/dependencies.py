from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.videos.repository import VideoRepository
from app.modules.videos.service import VideoMetadataService

def get_video_service(session: AsyncSession = Depends(get_db)) -> VideoMetadataService:
    repo = VideoRepository(session)
    return VideoMetadataService(repository=repo)