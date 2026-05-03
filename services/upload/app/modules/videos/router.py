import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.storage import S3Service
from app.modules.videos.schemas import VideoUploadResponse
from app.modules.videos.service import VideoUploadService
from app.modules.videos.repository import IVideoRepository, VideoUploadRepository

router = APIRouter(prefix="/videos", tags=["Videos"])

# --- ПРОВАЙДЕРИ (Фабрики об'єктів) ---

def get_s3_service() -> S3Service:
    return S3Service()

def get_video_repo(db: AsyncSession = Depends(get_db)) -> IVideoRepository:
    return VideoUploadRepository(db)

def get_video_service(
    repo: IVideoRepository = Depends(get_video_repo),
    s3_service: S3Service = Depends(get_s3_service),
    db: AsyncSession = Depends(get_db)
) -> VideoUploadService:
    return VideoUploadService(
        repo=repo,
        s3_service=s3_service,
        commit_func=db.commit,
        rollback_func=db.rollback
    )


# --- ЕНДПОІНТ ---

@router.post("/", response_model=VideoUploadResponse)
async def upload_video_endpoint(
    title: str = Form(...),
    video_id: uuid.UUID = Form(...),
    user_id: uuid.UUID = Form(...),
    file: UploadFile = File(...),
    video_service: VideoUploadService = Depends(get_video_service)
):
    try:
        return await video_service.process_upload(
            title=title, video_id=video_id, user_id=user_id, file=file
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=500, detail=str(re))