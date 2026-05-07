from fastapi import APIRouter, Depends, HTTPException, status
import uuid

from app.modules.videos.schemas import VideoBase, VideoRead, VideoUpdate
from app.modules.videos.service import VideoMetadataService
from app.modules.videos.dependencies import get_video_service
from app.common.types import UserTokenType

router = APIRouter(prefix="/videos", tags=["Videos"])


@router.post("/", response_model=VideoRead, status_code=status.HTTP_201_CREATED)
async def create_video_metadata(
    data: VideoBase,
    token_data: UserTokenType,
    service: VideoMetadataService = Depends(get_video_service),
):
    return await service.create_video(data=data, user_id=token_data.user_id)


@router.get("/{video_id}", response_model=VideoRead)
async def get_video(
    video_id: uuid.UUID,
    service: VideoMetadataService = Depends(get_video_service)
):
    video = await service.get_video(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


@router.get("/", response_model=list[VideoRead])
async def list_videos(
    limit: int = 20,
    offset: int = 0,
    service: VideoMetadataService = Depends(get_video_service)
):
    return await service.list_videos(limit=limit, offset=offset)


@router.patch("/{video_id}", response_model=VideoRead)
async def update_video(
    video_id: uuid.UUID,
    data: VideoUpdate,
    service: VideoMetadataService = Depends(get_video_service)
):
    try:
        return await service.update_metadata(video_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: uuid.UUID,
    service: VideoMetadataService = Depends(get_video_service)
):
    await service.delete_video(video_id)
    return None
