from typing import Optional
import logging

from fastapi import APIRouter, Depends, HTTPException
from app.config import settings
from app.database import get_db
from app.dependencies.auth import require_user_id
from app.schemas.job import TailorRequest, TailorResponse
from app.services.tailor import tailor_profile_for_job

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/tailor", tags=["tailor"])


@router.post("/", response_model=TailorResponse)
async def tailor(
    body: TailorRequest,
    db=Depends(get_db),
    user_id: Optional[str] = Depends(require_user_id),
):
    try:
        print(f"AUTH_REQUIRED={settings.auth_required}, user_id={user_id}")
        profile_query = (
            db.table("profiles")
            .select("*")
            .eq("id", str(body.profile_id))
        )
        if user_id:
            profile_query = profile_query.eq("user_id", user_id)
        profile_response = await profile_query.execute()
        if not profile_response.data:
            raise HTTPException(
                status_code=404,
                detail={"code": "PROFILE_NOT_FOUND", "message": "Profile not found"},
            )

        job_query = (
            db.table("job_descriptions")
            .select("*")
            .eq("id", str(body.job_id))
        )
        if user_id:
            job_query = job_query.eq("user_id", user_id)
        job_response = await job_query.execute()
        if not job_response.data:
            raise HTTPException(
                status_code=404,
                detail={"code": "JOB_NOT_FOUND", "message": "Job not found"},
            )

        profile = profile_response.data[0]
        job = job_response.data[0]

        if job.get("profile_id") != str(body.profile_id):
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "JOB_PROFILE_MISMATCH",
                    "message": "Job does not belong to this profile",
                },
            )

        result = tailor_profile_for_job(profile, job)
        return TailorResponse.model_validate(result)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Tailor failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))