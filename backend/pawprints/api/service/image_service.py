from datetime import UTC, datetime, timedelta
import json
import logging
import mimetypes
from typing import Annotated
import uuid

from botocore.client import BaseClient
from fastapi import Depends, UploadFile
import filetype
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from config import Config
from pawprints.database.media import S3_PUBLIC_ENDPOINT, get_s3_client
from pawprints.database.session import get_async_db_session
from pawprints.exceptions.images import ImageFileError, ImageFileTypeError
from pawprints.logger import get_logger
from pawprints.models.orm import Petition
from pawprints.models.schema import ReturnImageURI


class ImageService:
    def __init__(self, session: AsyncSession, s3_client: BaseClient, logger: logging.Logger):
        self.session = session
        self.s3_client = s3_client
        self.logger = logger
        self.config = Config()
        self.ALLOWED_TYPES = {"image/gif" "image/jpeg", "image/png", "image/webp", "image/jpeg"}

    def _extract_active_images(self, lexical_json: str) -> set[str]:
        """Recursively finds all image filenames in a Lexical JSON state."""
        active_filenames = set()
        if not lexical_json:
            return active_filenames

        try:
            data = json.loads(lexical_json)
        except json.JSONDecodeError:
            return active_filenames

        def traverse(node):
            if isinstance(node, dict):
                if node.get("type") == "image" and "src" in node:
                    filename = node["src"].split("/")[-1]
                    active_filenames.add(filename)

                # Dig into children
                for child in node.get("children", []):
                    traverse(child)

            elif isinstance(node, list):
                for item in node:
                    traverse(item)

        # Start traversal at the root
        if "root" in data:
            traverse(data["root"])

        return active_filenames

    async def run_garbage_collection(self, bucket: str = "images"):
        self.logger.info("Starting stateless image garbage collection...")
        active_filenames = set()

        try:
            # Filter out None descriptions right in the query
            stmt = select(Petition.description).where(Petition.description.isnot(None))
            result = await self.session.execute(stmt)
            descriptions = result.scalars().all()

            for d in descriptions:
                active_filenames.update(self._extract_active_images(d))

        except Exception as e:
            self.logger.error(f"DB Error during garbage collection: {e}")
            return

        try:
            # Wrap the synchronous Boto3 pagination in a threadpool function
            def fetch_all_s3_objects():
                paginator = self.s3_client.get_paginator("list_objects_v2")
                return list(paginator.paginate(Bucket=bucket))

            pages = await run_in_threadpool(fetch_all_s3_objects)

            cutoff_time = datetime.now(UTC) - timedelta(hours=24)
            deleted_count = 0

            for page in pages:
                for obj in page.get("Contents", []):
                    filename = obj["Key"]
                    last_modified = obj["LastModified"]

                    # Diff check
                    if filename not in active_filenames and last_modified < cutoff_time:
                        await self.delete_petition_image(filename=filename, bucket=bucket)
                        deleted_count += 1
                        self.logger.info(f"Swept orphaned image: {filename}")

            self.logger.info(f"GC Complete. Removed {deleted_count} orphaned images.")

        except Exception as e:
            self.logger.error(f"S3 Error during GC: {e}")

    async def validate_image(self, file: UploadFile):
        # Read the first 2048 bytes
        header = await file.read(2048)
        await file.seek(0)  # Reset pointer

        kind = filetype.guess(header)

        if kind is None or kind.mime not in self.ALLOWED_TYPES:
            raise ImageFileTypeError(message="Unsupported or invalid image type")

        return kind.mime

    async def upload_petition_image(
        self, *, file: UploadFile, bucket: str = "images"
    ) -> ReturnImageURI:
        # validate and get verified MIME type
        file_mime = await self.validate_image(file=file)
        ext = mimetypes.guess_extension(file_mime) or ".png"

        # generate secure filename
        hashed_name = f"{uuid.uuid4().hex}{ext}"

        try:
            await run_in_threadpool(
                self.s3_client.upload_fileobj,
                file.file,
                bucket,  # Use the parameter, not the hardcoded string
                hashed_name,
                ExtraArgs={"ContentType": file_mime},  # Use verified MIME
            )

            image_uri = f"{S3_PUBLIC_ENDPOINT}/{bucket}/{hashed_name}"
            self.logger.info(f"Image location: {image_uri}")

            return ReturnImageURI(uri=image_uri)
        except Exception as e:
            self.logger.error(f"Failed to upload image: {e}")
            raise ImageFileError("Image failed to upload")

    async def delete_petition_image(self, *, filename: str, bucket: str = "images"):
        try:
            await run_in_threadpool(self.s3_client.delete_object, Bucket=bucket, Key=filename)

        except Exception as e:
            self.logger.error(f"Failed to delete image: {e}")
            raise ImageFileError("Image failed to delete")


def get_petition_service(
    session: Annotated[AsyncSession, Depends(get_async_db_session)],
    s3_client: Annotated[BaseClient, Depends(get_s3_client)],
    logger: Annotated[logging.Logger, Depends(get_logger)],
) -> ImageService:
    """Factory function to obtain a PetitionService instance."""
    return ImageService(session=session, s3_client=s3_client, logger=logger)


ImageServiceDep = Annotated[ImageService, Depends(get_petition_service)]
