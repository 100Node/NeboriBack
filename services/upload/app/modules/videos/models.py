import uuid
from datetime import datetime
from sqlalchemy import String, func, Enum as SQLEnum, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base
from app.modules.videos.enums import VideoStatusEnum


class VideoUpload(Base):
    __tablename__ = "video_uploads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    video_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False) # video_id from metadata_service
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255))
    filename: Mapped[str] = mapped_column(String(255))
    s3_path: Mapped[str] = mapped_column(String(512))
    
    status: Mapped[VideoStatusEnum] = mapped_column(
        SQLEnum(
            VideoStatusEnum, 
            native_enum=False, 
            values_callable=lambda obj: [e.value for e in obj]
        ),
        default=VideoStatusEnum.PENDING,
        server_default=text("'pending'"),
        nullable=False,
        index=True
    )
    
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=func.now(), nullable=True)