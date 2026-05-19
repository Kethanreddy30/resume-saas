from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class UploadStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PARSED = "PARSED"
    FAILED = "FAILED"


class UploadResponse(BaseModel):
    id: str
    profile_id: Optional[str] = None
    file_name: str
    file_path: str
    file_type: str
    status: UploadStatus
    parsed_data: Optional[dict] = None
    error_msg: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None