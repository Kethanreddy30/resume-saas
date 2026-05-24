from app.services.llm_provider import LLMProvider


def tailor_profile_for_job(profile: dict, job: dict) -> dict:
    """Generate localized tailoring suggestions for a profile vs job."""
    provider = LLMProvider()
    return provider.compare(profile, job)
