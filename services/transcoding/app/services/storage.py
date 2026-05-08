import mimetypes
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
        self._verified_buckets: set[str] = set()

    async def ensure_bucket_exists(self, bucket_name: str) -> None:
        if bucket_name in self._verified_buckets:
            return
        async with self.session.client("s3", endpoint_url=self.endpoint_url) as client:  # type: ignore
            try:
                await client.head_bucket(Bucket=bucket_name)
                self._verified_buckets.add(bucket_name)
            except ClientError as e:
                error_code = e.response["Error"]["Code"]
                if error_code == "404" or error_code == "NoSuchBucket":
                    logger.info(f"Bucket '{bucket_name}' not found. Creating...")
                    await client.create_bucket(Bucket=bucket_name)
                    self._verified_buckets.add(bucket_name)
                else:
                    logger.error(f"Failed to verify bucket: {e}")
                    raise

    async def download_video(self, bucket_name: str, object_name: str, local_file_path: str) -> str:
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        await self.ensure_bucket_exists(bucket_name)
        async with self.session.client("s3", endpoint_url=self.endpoint_url) as client:  # type: ignore
            try:
                logger.info(f"Downloading {object_name} from {bucket_name} to {local_file_path}...")
                await client.download_file(bucket_name, object_name, local_file_path)
                logger.info(f"Successfully downloaded to {local_file_path}")
                return local_file_path
            except ClientError as e:
                logger.error(f"S3 Download error for {object_name}: {e}")
                raise RuntimeError(f"Failed to download {object_name} from S3.")

    async def upload_file(self, bucket_name: str, object_name: str, local_file_path: str, content_type: str = "video/mp4") -> str:
        await self.ensure_bucket_exists(bucket_name)
        async with self.session.client("s3", endpoint_url=self.endpoint_url) as client:  # type: ignore
            try:
                logger.info(f"Uploading {local_file_path} to {bucket_name}/{object_name}...")
                await client.upload_file(
                    local_file_path,
                    bucket_name,
                    object_name,
                    ExtraArgs={"ContentType": content_type}
                )
                logger.info(f"Successfully uploaded {object_name}")
                return object_name
            except ClientError as e:
                logger.error(f"S3 Upload error for {object_name}: {e}")
                raise RuntimeError(f"Failed to upload {object_name} to S3.")

    async def upload_directory(self, local_dir: str, s3_prefix: str, bucket_name: str):
        if not os.path.isdir(local_dir):
            logger.error(f"Directory not found: {local_dir}")
            return
        for root, _, files in os.walk(local_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, local_dir)
                s3_object_name = f"{s3_prefix}/{relative_path}"
                content_type, _ = mimetypes.guess_type(local_path)
                if not content_type:
                    if local_path.endswith(".m3u8"):
                        content_type = "application/vnd.apple.mpegurl"
                    elif local_path.endswith(".ts"):
                        content_type = "video/mp2t"
                    else:
                        content_type = "application/octet-stream"
                await self.upload_file(
                    bucket_name=bucket_name,
                    object_name=s3_object_name,
                    local_file_path=local_path,
                    content_type=content_type,
                )

    async def delete_prefix(self, bucket_name: str, prefix: str) -> None:
        """Видаляє всі об'єкти в bucket під вказаним префіксом (папкою)."""
        async with self.session.client("s3", endpoint_url=self.endpoint_url) as client:  # type: ignore
            try:
                paginator = client.get_paginator("list_objects_v2")
                async for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
                    objects = page.get("Contents", [])
                    if not objects:
                        continue
                    delete_payload = {"Objects": [{"Key": obj["Key"]} for obj in objects]}
                    await client.delete_objects(Bucket=bucket_name, Delete=delete_payload)
                    logger.info(f"Deleted {len(objects)} objects under {bucket_name}/{prefix}")
            except ClientError as e:
                logger.error(f"Error deleting prefix {prefix} from {bucket_name}: {e}")
                raise RuntimeError(f"Failed to delete prefix {prefix}: {str(e)}")