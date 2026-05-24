from datetime import datetime, timezone
from io import BytesIO
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from postgrest.exceptions import APIError

from app.database import get_db
from app.dependencies.auth import require_user_id
from app.schemas.profile import (
    PopulateFromUploadRequest,
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
    ProfileUploadsResponse,
)
from app.schemas.upload import UploadResponse, UploadStatus
from app.services.pdf_export import render_profile_pdf
from app.services.profile_merge import merge_parsed_into_profile

router = APIRouter(prefix="/api/v1/profiles", tags=["profiles"])


async def _get_profile_or_404(db, profile_id: str, user_id: str | None = None) -> dict:
    query = db.table("profiles").select("*").eq("id", profile_id)
    if user_id:
        query = query.eq("user_id", user_id)
    response = await query.execute()

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail={"code": "PROFILE_NOT_FOUND", "message": "Profile not found"},
        )

    return response.data[0]


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile: ProfileCreate,
    db=Depends(get_db),
    user_id: Optional[str] = Depends(require_user_id),
):
    try:
        payload = profile.model_dump()
        if user_id:
            payload["user_id"] = user_id
        response = await db.table("profiles").insert(payload).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create profile")

        return response.data[0]

    except HTTPException:
        raise
    except APIError as e:
        if "duplicate key" in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "EMAIL_EXISTS",
                    "message": "A profile with this email already exists",
                },
            )
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating profile: {str(e)}")


@router.get("/{profile_id}/uploads", response_model=ProfileUploadsResponse)
async def list_profile_uploads(
    profile_id: str,
    db=Depends(get_db),
    user_id: Optional[str] = Depends(require_user_id),
):
    await _get_profile_or_404(db, profile_id, user_id)

    query = (
        db.table("uploads")
        .select("*")
        .eq("profile_id", profile_id)
        .order("created_at", desc=True)
    )
    if user_id:
        query = query.eq("user_id", user_id)
    response = await query.execute()

    uploads = [UploadResponse(**row) for row in response.data]
    return ProfileUploadsResponse(uploads=uploads)


@router.post("/{profile_id}/populate-from-upload", response_model=ProfileResponse)
async def populate_from_upload(
    profile_id: str,
    body: PopulateFromUploadRequest,
    db=Depends(get_db),
    user_id: Optional[str] = Depends(require_user_id),
):
    profile = await _get_profile_or_404(db, profile_id, user_id)

    upload_query = db.table("uploads").select("*").eq("id", body.upload_id)
    if user_id:
        upload_query = upload_query.eq("user_id", user_id)
    upload_response = await upload_query.execute()
    if not upload_response.data:
        raise HTTPException(
            status_code=404,
            detail={"code": "UPLOAD_NOT_FOUND", "message": "Upload not found"},
        )

    upload = upload_response.data[0]

    if upload.get("status") != UploadStatus.PARSED.value:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "UPLOAD_NOT_READY",
                "message": "Upload must be in PARSED status before populating profile",
            },
        )

    upload_profile_id = upload.get("profile_id")
    if upload_profile_id and upload_profile_id != profile_id:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "UPLOAD_PROFILE_MISMATCH",
                "message": "Upload belongs to a different profile",
            },
        )

    if not upload_profile_id:
        await (
            db.table("uploads")
            .update({"profile_id": profile_id})
            .eq("id", body.upload_id)
            .execute()
        )

    parsed_data = upload.get("parsed_data") or {}
    update_data = merge_parsed_into_profile(profile, parsed_data)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

    if update_data:
        await (
            db.table("profiles")
            .update(update_data)
            .eq("id", profile_id)
            .execute()
        )

    updated = await (
        db.table("profiles").select("*").eq("id", profile_id).execute()
    )
    return updated.data[0]


@router.get("/{profile_id}/export/pdf")
async def export_profile_pdf(
    profile_id: str,
    db=Depends(get_db),
    user_id: Optional[str] = Depends(require_user_id),
):
    profile = await _get_profile_or_404(db, profile_id, user_id)

    try:
        pdf_bytes = render_profile_pdf(profile)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": "PDF_EXPORT_FAILED", "message": str(e)[:200]},
        )

    filename = f"{profile.get('full_name', 'resume').replace(' ', '-').lower()}-resume.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: str,
    db=Depends(get_db),
    user_id: Optional[str] = Depends(require_user_id),
):
    return await _get_profile_or_404(db, profile_id, user_id)


@router.patch("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: str,
    profile_update: ProfileUpdate,
    db=Depends(get_db),
    user_id: Optional[str] = Depends(require_user_id),
):
    await _get_profile_or_404(db, profile_id, user_id)

    update_data = profile_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await (
        db.table("profiles")
        .update(update_data)
        .eq("id", profile_id)
        .execute()
    )

    updated_profile = await (
        db.table("profiles").select("*").eq("id", profile_id).execute()
    )

    if not updated_profile.data:
        raise HTTPException(
            status_code=404,
            detail={"code": "PROFILE_NOT_FOUND", "message": "Profile not found"},
        )

    return updated_profile.data[0]


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: str,
    db=Depends(get_db),
    user_id: Optional[str] = Depends(require_user_id),
):
    await _get_profile_or_404(db, profile_id, user_id)

    await db.table("profiles").delete().eq("id", profile_id).execute()
    return
