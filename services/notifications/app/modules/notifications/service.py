import httpx
import uuid
import logging
from app.core.config import settings
from app.core.discovery import get_service_url

logger = logging.getLogger(__name__)

class NotificationService:
    async def get_achievements(self, user_id: int):
        try:
            # Discover achievements service
            base_url = get_service_url("achievements-service")
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{base_url}/achievements/user/{user_id}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch achievements: {e}")
            return []
