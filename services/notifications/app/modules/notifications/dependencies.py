from typing import Annotated
from fastapi import Depends
from app.modules.notifications.service import NotificationService
from app.common.types import UserTokenType, get_current_user

def get_notification_service() -> NotificationService:
    return NotificationService()

# Dependency to get current user from token
CurrentUser = Annotated[UserTokenType, Depends(get_current_user)]
