import logging
from faststream.rabbit import RabbitRouter
from app.modules.achievements.service import AchievementService
from app.modules.achievements.dependencies import get_achievement_service
from app.db.session import AsyncSessionLocal
from app.modules.achievements.repository import AchievementRepository
import uuid

logger = logging.getLogger(__name__)
router = RabbitRouter()

async def get_service() -> AchievementService:
    async with AsyncSessionLocal() as session:
        repo = AchievementRepository(session)
        return AchievementService(repo)

@router.subscriber("video.liked")
async def handle_video_liked(payload: dict):
    user_id = payload.get("user_id")
    video_id = payload.get("video_id")
    if user_id and video_id:
        service = await get_service()
        await service.process_like(int(user_id), video_id)
        logger.info(f"Processed like achievement for user {user_id}")
