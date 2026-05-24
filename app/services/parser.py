import json
import logging
import tempfile
import os
from groq import Groq
from app.config import settings

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


def extract_text_from_file(file_bytes: bytes, file_type: str) -> str:
    """Extract text from PDF or image using pymupdf4llm."""
    import pymupdf4llm
    import pymupdf

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf" if "pdf" in file_type else ".jpg"
    ) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        if "pdf" in file_type:
            text = pymupdf4llm.to_markdown(tmp_path)
        else:
            # Image: convert to PDF first then extract
            doc = pymupdf.open(tmp_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
        return text
    finally:
        os.unlink(tmp_path)


def parse_resume_with_ai(text: str) -> dict:
    """Send extracted text to Groq for structured extraction."""
    if len(text) > 6000:
        logger.warning("Resume text truncated from %d to 6000 chars", len(text))

    client = Groq(api_key=settings.groq_api_key)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": EXTRACTION_PROMPT + text[:6000]
            }
        ],
        temperature=0.1,
        max_tokens=2000,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown code blocks if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.error("Failed to parse AI response as JSON: %r", raw[:200])
        raise ValueError("AI returned invalid JSON; could not parse resume data") from None


def parse_resume(file_bytes: bytes, file_type: str) -> dict:
    """Full pipeline: extract text → AI structure → return dict."""
    text = extract_text_from_file(file_bytes, file_type)
    if not text or len(text.strip()) < 50:
        raise ValueError("Could not extract readable text from file")
    return parse_resume_with_ai(text)