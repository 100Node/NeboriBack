from fastapi import APIRouter, Depends, status
from app.modules.achievements.schemas import AchievementCreate, AchievementRead
from app.modules.achievements.service import AchievementService
from app.modules.achievements.dependencies import get_achievement_service
from app.common.types import UserTokenType

router = APIRouter(prefix="/achievements", tags=["Achievements"])

@router.post("/", response_model=AchievementRead, status_code=status.HTTP_201_CREATED)
async def create_achievement(
    data: AchievementCreate,
    token_data: UserTokenType,
    service: AchievementService = Depends(get_achievement_service),
):
    return await service.create_achievement(data=data, user_id=token_data.user_id)

@router.post("/like", status_code=status.HTTP_204_NO_CONTENT)
async def process_like_achievement(
    video_id: str,
    token_data: UserTokenType,
    service: AchievementService = Depends(get_achievement_service),
):
    await service.process_like(user_id=token_data.user_id, video_id=video_id)
    return None

@router.get("/user/{user_id}", response_model=list[AchievementRead])
async def get_user_achievements(
    user_id: int,
    service: AchievementService = Depends(get_achievement_service),
):
    return await service.get_user_achievements(user_id=user_id)
