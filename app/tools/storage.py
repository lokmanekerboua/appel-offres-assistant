import json
import logging
import uuid
from datetime import datetime, timezone

from botocore.exceptions import ClientError

from app.core.aws_client import s3_client
from app.core.config import settings

logger = logging.getLogger(__name__)


def save_analysis_to_s3(tender_text: str, analysis_result: dict) -> str | None:
    """
    Persists a tender analysis to S3, keyed by timestamp + uuid.
    Returns the S3 key, or None if the upload failed (non-blocking:
    storage failure should never break the API response).
    """
    key = f"analyses/{datetime.now(timezone.utc):%Y/%m/%d}/{uuid.uuid4()}.json"

    payload = {
        "tender_text": tender_text,
        "analysis": analysis_result,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        s3_client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=key,
            Body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            ContentType="application/json",
        )
        logger.info(f"analysis_saved_to_s3: {key}")
        return key
    except ClientError as e:
        logger.error(f"s3_upload_failed: {e}")
        return None


def save_pdf_report_to_s3(pdf_bytes: bytes) -> str | None:
    """
    Uploads a generated PDF report to S3. Returns the S3 key,
    or None if the upload failed (non-blocking).
    """
    key = f"reports/{datetime.now(timezone.utc):%Y/%m/%d}/{uuid.uuid4()}.pdf"

    try:
        s3_client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=key,
            Body=pdf_bytes,
            ContentType="application/pdf",
        )
        logger.info(f"pdf_report_saved_to_s3: {key}")
        return key
    except ClientError as e:
        logger.error(f"s3_pdf_upload_failed: {e}")
        return None


def generate_presigned_url(key: str, expires_in_seconds: int = 3600) -> str:
    """Generate a temporary URL for displaying or downloading a private PDF."""
    return s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": settings.s3_bucket_name,
            "Key": key,
            "ResponseContentDisposition": "inline",
        },
        ExpiresIn=expires_in_seconds,
        HttpMethod="GET",
    )
