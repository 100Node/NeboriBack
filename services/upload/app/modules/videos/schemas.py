from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class VideoUploadResponse(BaseModel):
    id: UUID
    video_id: UUID
    user_id: int
    title: str
    filename: str
    s3_path: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)