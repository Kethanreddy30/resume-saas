from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    profile_id: UUID
    title: str = Field(min_length=1, max_length=200)
    tagline: Optional[str] = None
    problem: Optional[str] = None
    solution: Optional[str] = None
    architecture: Optional[str] = None
    constraints: Optional[str] = None
    tradeoffs: Optional[str] = None
    lessons: List[dict] = Field(default_factory=list)
    tech_stack: List[str] = Field(default_factory=list)
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    featured: bool = False
    order_index: int = 0


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    tagline: Optional[str] = None
    problem: Optional[str] = None
    solution: Optional[str] = None
    architecture: Optional[str] = None
    constraints: Optional[str] = None
    tradeoffs: Optional[str] = None
    lessons: Optional[List[dict]] = None
    tech_stack: Optional[List[str]] = None
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    featured: Optional[bool] = None
    order_index: Optional[int] = None


class ProjectResponse(BaseModel):
    id: UUID
    profile_id: UUID
    title: str
    tagline: Optional[str] = None
    problem: Optional[str] = None
    solution: Optional[str] = None
    architecture: Optional[str] = None
    constraints: Optional[str] = None
    tradeoffs: Optional[str] = None
    lessons: List[dict] = Field(default_factory=list)
    tech_stack: List[str] = Field(default_factory=list)
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    featured: bool = False
    order_index: int = 0
    created_at: datetime
    updated_at: datetime