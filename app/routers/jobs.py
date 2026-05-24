from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from postgrest.exceptions import APIError

from app.database import get_db
from app.dependencies.auth import require_user_id
from app.schemas.job import JobCreate, JobResponse
from app.services.llm_provider import LLMProvider

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job: JobCreate,
    db=Depends(get_db),
    user_id: Optional[str] = Depends(require_user_id),
):
    profile_query = (
        db.table("profiles")
        .select("id")
        .eq("id", str(job.profile_id))
    )
    if user_id:
        profile_query = profile_query.eq("user_id", user_id)
    profile = await profile_query.execute()
    if not profile.data:
        raise HTTPException(
            status_code=404,
            detail={"code": "PROFILE_NOT_FOUND", "message": "Profile not found"},
        )

    provider = LLMProvider()
    requirements = provider.extract_job_requirements(job.description)

    payload = {
        "profile_id": str(job.profile_id),
        "company": job.company,
        "role": job.role,
        "description": job.description,
        "requirements": requirements,
    }
    if user_id:
        payload["user_id"] = user_id

    try:
        response = await db.table("job_descriptions").insert(payload).execute()
    except APIError as e:
        if "job_descriptions" in str(e):
            raise HTTPException(
                status_code=503,
                detail={
                    "code": "MIGRATION_REQUIRED",
                    "message": "Run migrations/001_job_descriptions.sql in Supabase first",
                },
            ) from e
        raise HTTPException(status_code=500, detail=str(e)) from e

    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create job description")

    return response.data[0]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    db=Depends(get_db),
    user_id: Optional[str] = Depends(require_user_id),
):
    query = db.table("job_descriptions").select("*").eq("id", job_id)
    if user_id:
        query = query.eq("user_id", user_id)
    response = await query.execute()
    if not response.data:
        raise HTTPException(
            status_code=404,
            detail={"code": "JOB_NOT_FOUND", "message": "Job description not found"},
        )
    return response.data[0]
