from fastapi import APIRouter, Depends, HTTPException
from app.modules.notifications.service import NotificationService
from app.modules.notifications.dependencies import get_notification_service, CurrentUser

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/achievements")
async def get_user_achievements(
    user_data: CurrentUser,
    service: NotificationService = Depends(get_notification_service),
):
    return await service.get_achievements(user_id=user_data.user_id)
