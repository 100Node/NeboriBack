import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, Enum as SQLEnum, UniqueConstraint, Index, text as sqltext
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.modules.videos.enums import CommentStatus, ReactionType, VideoStatus


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(index=True)

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    thumbnail_url: Mapped[str | None] = mapped_column(String, nullable=True)
    playlist_url: Mapped[str | None] = mapped_column(String, nullable=True)

    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    views_count: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[VideoStatus] = mapped_column(
        SQLEnum(
            VideoStatus,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj]
        ),
        default=VideoStatus.UPLOADING,
        server_default=sqltext("'uploading'"),
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(
        timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    # relations
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="video", cascade="all, delete-orphan")
    reactions: Mapped[list["VideoReaction"]] = relationship(
        back_populates="video", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    video_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("videos.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(index=True)
    text: Mapped[str] = mapped_column(Text)
    status: Mapped[CommentStatus] = mapped_column(
        SQLEnum(
            CommentStatus,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj]
        ),
        default=CommentStatus.ACTIVE,
        server_default=sqltext("'active'"),
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # relations
    video: Mapped["Video"] = relationship(back_populates="comments")


class VideoReaction(Base):
    __tablename__ = "video_reactions"
    __table_args__ = (
        UniqueConstraint("video_id", "user_id",
                         name="uix_video_user_reaction"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    video_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("videos.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(index=True)
    reaction_type: Mapped[ReactionType] = mapped_column(
        SQLEnum(
            ReactionType,
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj]
        ),
        nullable=False,
    )

    # relations
    video: Mapped["Video"] = relationship(back_populates="reactions")
