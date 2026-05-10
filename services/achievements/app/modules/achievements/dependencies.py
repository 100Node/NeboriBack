from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.modules.achievements.repository import AchievementRepository
from app.modules.achievements.service import AchievementService

async def get_achievement_repository(session: AsyncSession = Depends(get_session)) -> AchievementRepository:
    return AchievementRepository(session)

async def get_achievement_service(
    repository: AchievementRepository = Depends(get_achievement_repository)
) -> AchievementService:
    return AchievementService(repository)
