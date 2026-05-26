import logging
import os
import tempfile

import pytesseract
from PIL import Image

from app.config import settings
from app.services.llm_provider import LLMProvider

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """
You are a resume parser. Extract structured data from this resume text.
Return ONLY valid JSON with this exact structure, nothing else:

{
  "full_name": "string or null",
  "email": "string or null",
  "phone": "string or null",
  "summary": "string or null",
  "skills": ["skill1", "skill2"],
  "experience": [
    {
      "company": "string",
      "role": "string",
      "duration": "string",
      "description": "string"
    }
  ],
  "education": [
    {
      "institution": "string",
      "degree": "string",
      "year": "string"
    }
  ],
  "certifications": ["cert1", "cert2"]
}

Resume text:
"""


def _configure_tesseract() -> None:
    if settings.tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd


def extract_text_from_file(file_bytes: bytes, file_type: str) -> str:
    """Extract text from PDF or image."""
    import pymupdf
    import pymupdf4llm

    suffix = ".pdf" if "pdf" in file_type else ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        if "pdf" in file_type:
            return pymupdf4llm.to_markdown(tmp_path)

        _configure_tesseract()
        try:
            return pytesseract.image_to_string(Image.open(tmp_path))
        except pytesseract.TesseractNotFoundError as exc:
            raise ValueError(
                "Tesseract OCR is not installed. Install tesseract-ocr or set TESSERACT_CMD."
            ) from exc
    finally:
        os.unlink(tmp_path)


def parse_resume_with_ai(text: str) -> dict:
    """Send extracted text to LLM for structured extraction."""
    if len(text) > 6000:
        logger.warning("Resume text truncated from %d to 6000 chars", len(text))

    provider = LLMProvider()
    return provider.extract(text, EXTRACTION_PROMPT)


def parse_resume(file_bytes: bytes, file_type: str) -> dict:
    """Full pipeline: extract text → AI structure → return dict."""
    text = extract_text_from_file(file_bytes, file_type)
    if not text or len(text.strip()) < 50:
        raise ValueError("Could not extract readable text from file")
    return parse_resume_with_ai(text)
