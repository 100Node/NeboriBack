import uuid
from sqlalchemy import select
from app.common.repository import BaseRepository
from app.modules.achievements.models import Achievement

class AchievementRepository(BaseRepository[Achievement]):
    def __init__(self, session):
        super().__init__(Achievement, session)

    async def find_by_user_and_type(self, user_id: int, achievement_type: str) -> Achievement | None:
        stmt = select(Achievement).where(
            Achievement.user_id == user_id,
            Achievement.type == achievement_type
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: int) -> list[Achievement]:
        stmt = select(Achievement).where(Achievement.user_id == user_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
