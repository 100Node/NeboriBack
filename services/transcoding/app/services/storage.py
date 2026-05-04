import os
import logging
import aioboto3
from botocore.exceptions import ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)

class S3TranscodeService:
    def __init__(self):
        self.session = aioboto3.Session(
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        )
        self.endpoint_url = settings.S3_ENDPOINT_URL

    async def download_video(self, bucket_name: str, object_name: str, local_file_path: str) -> str:
        """
        Завантажує файл з MinIO на локальний диск контейнера.
        """
        # Переконуємось, що папка для файлу існує (наприклад /tmp/nebori/...)
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        # type: ignore
        async with self.session.client("s3", endpoint_url=self.endpoint_url) as client: # type: ignore
            try:
                logger.info(f"Downloading {object_name} from {bucket_name} to {local_file_path}...")
                
                # aioboto3 сам розіб'є файл на чанки і асинхронно запише на диск
                await client.download_file(bucket_name, object_name, local_file_path)
                
                logger.info(f"Successfully downloaded to {local_file_path}")
                return local_file_path
            
            except ClientError as e:
                logger.error(f"S3 Download error for {object_name}: {e}")
                raise RuntimeError(f"Failed to download {object_name} from S3.")
            
    async def upload_file(self, bucket_name: str, object_name: str, local_file_path: str, content_type: str = "video/mp4") -> str:
        """
        Завантажує готовий файл з диска контейнера назад у MinIO.
        """
        # type: ignore
        async with self.session.client("s3", endpoint_url=self.endpoint_url) as client: # type: ignore
            try:
                logger.info(f"Uploading {local_file_path} to {bucket_name}/{object_name}...")
                
                await client.upload_file(
                    local_file_path, 
                    bucket_name, 
                    object_name,
                    ExtraArgs={'ContentType': content_type}
                )
                
                logger.info(f"Successfully uploaded {object_name}")
                return object_name
            
            except ClientError as e:
                logger.error(f"S3 Upload error for {object_name}: {e}")
                raise RuntimeError(f"Failed to upload {object_name} to S3.")