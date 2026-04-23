from collections.abc import Generator
import json
import logging

import boto3
from botocore.client import BaseClient, Config as botocoreConfig
from botocore.exceptions import ClientError

from config import Config

logger = logging.getLogger("pawprints.media")

config = Config()

# Constants
S3_ENDPOINT = f"{config.MINIO_URL}"
S3_PUBLIC_ENDPOINT = f"{config.MINIO_PUBLIC_URL}"
S3_ACCESS_KEY = config.S3USER
S3_SECRET_KEY = config.S3PASSWORD


def get_s3_client() -> Generator[BaseClient, None, None]:
    """Factory function to obtain an S3 client instance."""
    client = boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        config=botocoreConfig(signature_version="s3v4"),
        region_name="us-east-1",
    )
    try:
        yield client
    finally:
        pass


def ensure_bucket_exists(bucket_name: str = "images") -> None:
    """Checks if a bucket exists, creates it if it doesn't, and sets it to public read."""
    client = boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        config=botocoreConfig(signature_version="s3v4"),
        region_name="us-east-1",
    )

    try:
        client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        error_code = int(e.response.get("Error", {}).get("Code", 0))
        if error_code == 404:
            logger.info("Bucket '%s' not found. Creating it now...", bucket_name)
            client.create_bucket(Bucket=bucket_name)

            # Define the Public Read policy
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*",
                    }
                ],
            }

            # Apply the policy to the newly created bucket
            client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))
            logger.info("Bucket '%s' created and set to public read.", bucket_name)
        else:
            raise
