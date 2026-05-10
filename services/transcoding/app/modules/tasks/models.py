import uuid
from datetime import datetime
from sqlalchemy import Integer, String, func, Enum as SQLEnum, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base
from app.modules.tasks.enums import TaskTypeEnum, TaskStatusEnum


class ProcessingTask(Base):
    __tablename__ = "processing_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)  # ID з metadata-service

    task_type: Mapped[TaskTypeEnum] = mapped_column(String(50))
    status: Mapped[TaskStatusEnum] = mapped_column(
        SQLEnum(
            TaskStatusEnum,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj]
        ),
        default=TaskStatusEnum.PENDING,
        server_default=text("'pending'"),
        nullable=False,
        index=True
    )

    original_file_path: Mapped[str] = mapped_column(String(512))
    progress: Mapped[int] = mapped_column(Integer, default=0)

    worker_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_log: Mapped[str | None] = mapped_column(String, nullable=True)

    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=func.now(), nullable=True)
