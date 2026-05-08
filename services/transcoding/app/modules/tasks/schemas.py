import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


class StreamItem(BaseModel):
    resolution: str
    url: str


class VideoUploadedPayload(BaseModel):
    video_id: uuid.UUID
    user_id: int
    s3_bucket: str
    s3_path: str


class VideoUploadedEvent(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: str = "video.uploaded"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: VideoUploadedPayload


class VideoProcessedPayload(BaseModel):
    video_id: uuid.UUID
    streams: list[StreamItem]
    duration: int | None = None


class VideoProcessedEvent(BaseModel):
    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: str = "video.processed"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: VideoProcessedPayload


class VideoCanceledPayload(BaseModel):
    video_id: uuid.UUID


class VideoCanceledEvent(BaseModel):
    payload: VideoCanceledPayload


class VideoDeletedPayload(BaseModel):
    video_id: uuid.UUID
    user_id: int  # потрібен щоб знайти папку в S3: {user_id}/{video_id}/


class VideoDeletedEvent(BaseModel):
    model_config = ConfigDict(extra='ignore')
    payload: VideoDeletedPayload