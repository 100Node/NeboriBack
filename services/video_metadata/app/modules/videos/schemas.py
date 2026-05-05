from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict

from app.modules.videos.enums import VideoStatus

# 1. Successful transcoding event
class VideoProcessedPayload(BaseModel):
    video_id: uuid.UUID
    hls_url: str  # Шлях до головного .m3u8 файлу в S3
    duration: int | None = None

class VideoProcessedEvent(BaseModel):
    payload: VideoProcessedPayload

# 2. Transcoding error event
class VideoFailedPayload(BaseModel):
    video_id: uuid.UUID
    error_message: str

class VideoFailedEvent(BaseModel):
    payload: VideoFailedPayload

# 3. Video Deletion Event
class VideoDeletedPayload(BaseModel):
    video_id: uuid.UUID

class VideoDeletedEvent(BaseModel):
    payload: VideoDeletedPayload

# 4. Video processing/upload cancellation event
class VideoCanceledPayload(BaseModel):
    video_id: uuid.UUID

class VideoCanceledEvent(BaseModel):
    payload: VideoCanceledPayload

class VideoBase(BaseModel):
    title: str
    description: str | None = None
    # category_id: int | None = None

class VideoCreate(VideoBase):
    user_id: uuid.UUID

class VideoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    # category_id: int | None = None
    status: VideoStatus | None = None

class VideoRead(VideoBase):
    id: uuid.UUID
    user_id: uuid.UUID
    status: VideoStatus
    playlist_url: str | None
    thumbnail_url: str | None
    duration: int | None
    views_count: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)