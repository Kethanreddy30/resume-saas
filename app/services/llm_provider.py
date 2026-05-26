import json
import logging
from groq import Groq
from app.config import settings

logger = logging.getLogger(__name__)
GROQ_MODEL = "llama-3.3-70b-versatile"

JOB_REQUIREMENTS_PROMPT = """
Extract structured job requirements from this job description.
Return ONLY valid JSON with this exact structure, nothing else:
{
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill1"],
  "keywords": ["keyword1", "keyword2"],
  "years_experience": "string or null",
  "education_requirement": "string or null"
}
Job description:
"""

TAILOR_PROMPT = """
Compare this candidate profile against the job requirements.
Return ONLY valid JSON with localized suggestions - do NOT rewrite the full resume.
{{
  "missing_skills": ["skill1"],
  "suggested_summary_additions": "1-2 sentences to add to summary",
  "keyword_gaps": ["keyword1"],
  "experience_tweaks": [
    {{
      "company": "string",
      "suggestion": "specific tweak for this role"
    }}
  ]
}}
Profile:
{profile}
Job requirements:
{requirements}
"""

class LLMProvider:
    def __init__(self, provider: str | None = None):
        self.provider = provider or settings.llm_provider

    def extract(self, text: str, prompt: str) -> dict:
        if self.provider == "groq":
            return self._groq_call(text, prompt)
        if self.provider == "ollama":
            return self._ollama_call(text, prompt)
        if self.provider == "deepseek":
            return self._deepseek_call(text, prompt)
        raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def extract_job_requirements(self, description: str) -> dict:
        return self.extract(description[:6000], JOB_REQUIREMENTS_PROMPT)

    def compare(self, profile: dict, job: dict) -> dict:
        requirements = job.get("requirements") or {}
        profile_summary = {
            "full_name": profile.get("full_name"),
            "summary": profile.get("summary"),
            "skills": profile.get("skills", []),
            "experience": profile.get("experience", [])[:5],
            "education": profile.get("education", [])[:3],
        }
        prompt = TAILOR_PROMPT.format(
            profile=json.dumps(profile_summary, indent=2),
            requirements=json.dumps(requirements, indent=2),
        )
        return self.extract("", prompt)

    def _groq_call(self, text: str, prompt: str) -> dict:
        client = Groq(api_key=settings.groq_api_key)
        content = prompt + text[:6000] if text else prompt
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": content}],
            temperature=0.1,
            max_tokens=2000,
        )
        raw = response.choices[0].message.content.strip()
        return self._parse_json_response(raw)

    def _ollama_call(self, text: str, prompt: str) -> dict:
        raise NotImplementedError("Ollama provider not configured yet")

    def _deepseek_call(self, text: str, prompt: str) -> dict:
        raise NotImplementedError("DeepSeek provider not configured yet")

    def _parse_json_response(self, raw: str) -> dict:
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.error("Failed to parse AI response as JSON: %r", raw[:200])
            raise ValueError("AI returned invalid JSON") from None