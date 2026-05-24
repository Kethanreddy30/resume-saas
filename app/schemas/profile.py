from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.upload import UploadResponse


class ProfileCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[dict] = Field(default_factory=list)
    education: List[dict] = Field(default_factory=list)


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    summary: Optional[str] = None
    skills: Optional[List[str]] = None
    experience: Optional[List[dict]] = None
    education: Optional[List[dict]] = None


class ProfileResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[dict] = Field(default_factory=list)
    education: List[dict] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class PopulateFromUploadRequest(BaseModel):
    upload_id: str


class ProfileUploadsResponse(BaseModel):
    uploads: List[UploadResponse]
