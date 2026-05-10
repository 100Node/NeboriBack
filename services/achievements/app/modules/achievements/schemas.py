from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class AchievementBase(BaseModel):
    type: str
    title: str
    description: str | None = None

class AchievementCreate(AchievementBase):
    pass

class AchievementRead(AchievementBase):
    id: UUID
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
