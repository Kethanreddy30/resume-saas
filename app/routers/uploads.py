import logging
import uuid
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile

from app.database import get_db
from app.dependencies.auth import require_user_id
from app.schemas.upload import UploadResponse, UploadStatus
from app.services.parser import parse_resume

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/uploads", tags=["uploads"])

ALLOWED_TYPES = {"application/pdf", "image/jpeg", "image/jpg", "image/png"}
MAX_SIZE_BYTES = 5 * 1024 * 1024


def process_resume_background(upload_id: str, file_bytes: bytes, file_type: str):
    from app.database import get_supabase_sync

    supabase = get_supabase_sync()
    try:
        supabase.table("uploads").update(
            {"status": UploadStatus.PROCESSING.value}
        ).eq("id", upload_id).execute()

        parsed_data = parse_resume(file_bytes, file_type)

        supabase.table("uploads").update(
            {
                "status": UploadStatus.PARSED.value,
                "parsed_data": parsed_data,
            }
        ).eq("id", upload_id).execute()

        logger.info("Resume parsed: %s", upload_id)

    except Exception as e:
        try:
            supabase.table("uploads").update(
                {
                    "status": UploadStatus.FAILED.value,
                    "error_msg": str(e)[:500],
                }
            ).eq("id", upload_id).execute()
        except Exception as update_err:
            logger.error(
                "Failed to mark upload %s as FAILED: %s",
                upload_id,
                str(update_err),
            )
        logger.error("Parse failed: %s — %s", upload_id, str(e))


@router.post("/resume", response_model=UploadResponse, status_code=202)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    profile_id: Optional[str] = None,
    db=Depends(get_db),
    user_id: Optional[str] = Depends(require_user_id),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INVALID_FILE_TYPE",
                "message": f"Allowed: PDF, JPEG, PNG. Got: {file.content_type}",
            },
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=422,
            detail={"code": "FILE_TOO_LARGE", "message": "Max 5MB"},
        )

    unique_prefix = str(uuid.uuid4())[:8]
    if user_id:
        file_path = f"resumes/{user_id}/{unique_prefix}_{file.filename}"
    else:
        file_path = f"resumes/{unique_prefix}_{file.filename}"

    try:
        await db.storage.from_("resumes").upload(
            path=file_path,
            file=file_bytes,
            file_options={"content-type": file.content_type},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": "STORAGE_ERROR", "message": str(e)[:200]},
        )

    data = {
        "file_name": file.filename,
        "file_path": file_path,
        "file_type": file.content_type,
        "status": UploadStatus.UPLOADED.value,
    }
    if user_id:
        data["user_id"] = user_id
    if profile_id:
        data["profile_id"] = profile_id

    response = await db.table("uploads").insert(data).execute()
    upload = response.data[0]

    background_tasks.add_task(
        process_resume_background,
        upload["id"],
        file_bytes,
        file.content_type,
    )

    return upload


@router.get("/{upload_id}", response_model=UploadResponse)
async def get_upload(
    upload_id: str,
    db=Depends(get_db),
    user_id: Optional[str] = Depends(require_user_id),
):
    query = db.table("uploads").select("*").eq("id", upload_id)
    if user_id:
        query = query.eq("user_id", user_id)
    response = await query.execute()
    if not response.data:
        raise HTTPException(
            status_code=404,
            detail={"code": "UPLOAD_NOT_FOUND", "message": "Upload not found"},
        )
    return response.data[0]
