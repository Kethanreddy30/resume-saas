from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    groq_api_key: str
    environment: str = "development"
    llm_provider: str = "groq"
    tesseract_cmd: Optional[str] = None
    auth_required: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
