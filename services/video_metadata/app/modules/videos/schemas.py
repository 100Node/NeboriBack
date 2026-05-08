from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Any
from app.modules.videos.enums import VideoStatusEnum


class StreamItem(BaseModel):
    resolution: str
    url: str


class VideoProcessedPayload(BaseModel):
    video_id: uuid.UUID
    streams: list[StreamItem]
    duration: int | None = None


class VideoProcessedEvent(BaseModel):
    model_config = ConfigDict(extra='ignore')
    payload: VideoProcessedPayload


class VideoFailedPayload(BaseModel):
    video_id: uuid.UUID
    error_message: str = ""


class VideoFailedEvent(BaseModel):
    model_config = ConfigDict(extra='ignore')
    payload: VideoFailedPayload


class VideoUploadStartedPayload(BaseModel):
    video_id: uuid.UUID


class VideoUploadStartedEvent(BaseModel):
    model_config = ConfigDict(extra='ignore')
    payload: VideoUploadStartedPayload


class VideoTranscodingStartedPayload(BaseModel):
    video_id: uuid.UUID


class VideoTranscodingStartedEvent(BaseModel):
    model_config = ConfigDict(extra='ignore')
    payload: VideoTranscodingStartedPayload


class VideoDeletedPayload(BaseModel):
    video_id: uuid.UUID
    user_id: int


class VideoDeletedEvent(BaseModel):
    model_config = ConfigDict(extra='ignore')
    payload: VideoDeletedPayload


class VideoBase(BaseModel):
    title: str
    description: str | None = None


class VideoUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class VideoRead(VideoBase):
    id: uuid.UUID
    user_id: int
    status: VideoStatusEnum
    streams: dict[str, str] = Field(default_factory=dict, alias="hls_urls")
    thumbnail_url: str | None
    duration: int | None
    views_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @field_validator("streams", mode="before")
    @classmethod
    def convert_hls_list_to_dict(cls, v: Any) -> dict[str, str]:
        if isinstance(v, list):
            return {item.resolution: item.url for item in v}
        return v