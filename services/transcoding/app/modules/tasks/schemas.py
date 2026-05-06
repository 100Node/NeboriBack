import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class VideoUploadedPayload(BaseModel):
    video_id: uuid.UUID
    user_id: uuid.UUID
    s3_bucket: str
    s3_path: str


class VideoUploadedEvent(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: str = "video.uploaded"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: VideoUploadedPayload


class VideoProcessedPayload(BaseModel):
    video_id: uuid.UUID
    audio_path: str
    video_1080p_path: str
    video_720p_path: str


class VideoProcessedEvent(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: str = "video.processed"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: VideoProcessedPayload


class VideoCanceledPayload(BaseModel):
    video_id: uuid.UUID

class VideoCanceledEvent(BaseModel):
    payload: VideoCanceledPayload