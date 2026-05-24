from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    profile_id: UUID
    company: str = Field(min_length=1, max_length=200)
    role: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=10)


class JobResponse(BaseModel):
    id: UUID
    profile_id: UUID
    company: str
    role: str
    description: str
    requirements: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class TailorRequest(BaseModel):
    profile_id: UUID
    job_id: UUID


class ExperienceTweak(BaseModel):
    company: str
    suggestion: str


class TailorResponse(BaseModel):
    missing_skills: List[str] = Field(default_factory=list)
    suggested_summary_additions: Optional[str] = None
    keyword_gaps: List[str] = Field(default_factory=list)
    experience_tweaks: List[ExperienceTweak] = Field(default_factory=list)
