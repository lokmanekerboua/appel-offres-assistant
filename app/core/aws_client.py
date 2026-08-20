import logging

import boto3
from botocore.config import Config

from app.core.config import settings

logger = logging.getLogger(__name__)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region,
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "virtual"},
    ),
)

textract_client = boto3.client(
    "textract",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region,
)
