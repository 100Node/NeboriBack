import logging
from typing import BinaryIO
import aioboto3
from botocore.exceptions import ClientError

from app.core.config import settings

logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self):
        self.session = aioboto3.Session(
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        )
        self.endpoint_url = settings.S3_ENDPOINT_URL
        self.bucket_name = settings.S3_BUCKET_NAME

    async def ensure_bucket_exists(self) -> None:
        async with self.session.client("s3", endpoint_url=self.endpoint_url) as client:  # type: ignore
            try:
                await client.head_bucket(Bucket=self.bucket_name)
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "404":
                    logger.info(f"Bucket '{self.bucket_name}' not found. Creating...")
                    await client.create_bucket(Bucket=self.bucket_name)
                else:
                    logger.error(f"Failed to verify bucket: {e}")
                    raise

    async def upload_video(self, file_obj: BinaryIO, object_name: str, content_type: str = "video/mp4") -> str:
        async with self.session.client("s3", endpoint_url=self.endpoint_url) as client:  # type: ignore
            try:
                await client.upload_fileobj(
                    Fileobj=file_obj,
                    Bucket=self.bucket_name,
                    Key=object_name,
                    ExtraArgs={"ContentType": content_type}
                )
                logger.info(f"Successfully uploaded {object_name} to {self.bucket_name}")
                return f"{self.bucket_name}/{object_name}"
            except ClientError as e:
                logger.error(f"Error uploading file to S3: {e}")
                raise Exception(f"S3 Upload failed: {str(e)}")

    async def delete_video(self, object_name: str) -> None:
        async with self.session.client("s3", endpoint_url=self.endpoint_url) as client:  # type: ignore
            try:
                await client.delete_object(Bucket=self.bucket_name, Key=object_name)
                logger.info(f"Deleted {object_name} from {self.bucket_name}")
            except ClientError as e:
                logger.error(f"Error deleting file from S3: {e}")
                raise Exception(f"S3 Delete failed: {str(e)}")