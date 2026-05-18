from datetime import datetime
from uuid import UUID
from typing import List, Optional

from pydantic import BaseModel, Field


class ProfileCreate(BaseModel):
    full_name: str
    email: str
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[dict] = Field(default_factory=list)
    education: List[dict] = Field(default_factory=list)


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    summary: Optional[str] = None
    skills: Optional[List[str]] = None
    experience: Optional[List[dict]] = None
    education: Optional[List[dict]] = None


class ProfileResponse(BaseModel):
    id: UUID
    full_name: str
    email: str
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[dict] = Field(default_factory=list)
    education: List[dict] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime