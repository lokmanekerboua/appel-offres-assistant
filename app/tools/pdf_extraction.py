import logging
from io import BytesIO

from pypdf import PdfReader

from app.core.aws_client import textract_client

logger = logging.getLogger(__name__)


def _extract_with_textract(pdf_bytes: bytes) -> str:
    """Uses AWS Textract OCR. Works even on scanned/image PDFs."""
    response = textract_client.detect_document_text(Document={"Bytes": pdf_bytes})
    lines = [
        block["Text"]
        for block in response.get("Blocks", [])
        if block["BlockType"] == "LINE"
    ]
    return "\n".join(lines)


def _extract_with_pypdf(pdf_bytes: bytes) -> str:
    """Local fallback extraction. Works for native (non-scanned) PDFs."""
    reader = PdfReader(BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Tries AWS Textract first. Falls back to local pypdf extraction on
    ANY failure (account not activated, subscription required, network
    issue, quota exceeded, etc.) so the pipeline never blocks on an
    external service being unavailable.
    """
    try:
        text = _extract_with_textract(pdf_bytes)
        logger.info("pdf_text_extracted_via_textract")
        return text
    except Exception as e:
        logger.warning(f"textract_unavailable_falling_back_to_pypdf: {e}")
        text = _extract_with_pypdf(pdf_bytes)
        logger.info("pdf_text_extracted_via_pypdf_fallback")
        return text