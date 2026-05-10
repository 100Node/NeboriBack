import uuid
from app.modules.achievements.repository import AchievementRepository
from app.modules.achievements.models import Achievement
from app.modules.achievements.schemas import AchievementCreate

class AchievementService:
    def __init__(self, repository: AchievementRepository):
        self.repository = repository

    async def create_achievement(self, data: AchievementCreate, user_id: int) -> Achievement:
        achievement_data = data.model_dump()
        achievement_data["user_id"] = user_id
        return await self.repository.create(achievement_data, commit=True)

    async def process_like(self, user_id: int, video_id: str) -> None:
        # Simple logic: first like gives an achievement
        existing = await self.repository.find_by_user_and_type(user_id, "first_like")
        if not existing:
            await self.repository.create({
                "user_id": user_id,
                "type": "first_like",
                "title": "First Like!",
                "description": f"You liked your first video: {video_id}"
            }, commit=True)

    async def get_user_achievements(self, user_id: int) -> list[Achievement]:
        return await self.repository.get_by_user(user_id)
