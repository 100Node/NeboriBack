from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class VideoUploadResponse(BaseModel):
    id: UUID
    video_id: UUID
    user_id: UUID
    title: str
    filename: str
    s3_path: str
    status: str
    created_at: datetime

    # Дозволяє Pydantic читати дані безпосередньо з об'єктів SQLAlchemy
    model_config = ConfigDict(from_attributes=True)