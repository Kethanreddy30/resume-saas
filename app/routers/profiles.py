from fastapi import APIRouter, Depends, HTTPException, status
from postgrest.exceptions import APIError
from app.database import get_db
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from datetime import datetime, timezone
router = APIRouter(prefix="/api/v1/profiles", tags=["profiles"])

@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: str,
    db=Depends(get_db),
):
    response = await (
        db.table("profiles")
        .select("*")
        .eq("id", profile_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "PROFILE_NOT_FOUND",
                "message": "Profile not found",
            },
        )

    return response.data[0]
@router.patch("/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: str,
    profile_update: ProfileUpdate,
    db=Depends(get_db),
):
    update_data = profile_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await (
        db.table("profiles")
        .update(update_data)
        .eq("id", profile_id)
        .execute()
    )

    updated_profile = await (
        db.table("profiles")
        .select("*")
        .eq("id", profile_id)
        .execute()
    )

    if not updated_profile.data:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "PROFILE_NOT_FOUND",
                "message": "Profile not found",
            },
        )

    return updated_profile.data[0]
@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: str,
    db=Depends(get_db),
):
    existing = await (
        db.table("profiles")
        .select("id")
        .eq("id", profile_id)
        .execute()
    )

    if not existing.data:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "PROFILE_NOT_FOUND",
                "message": "Profile not found",
            },
        )

    await (
        db.table("profiles")
        .delete()
        .eq("id", profile_id)
        .execute()
    )

    return
@router.post(
    "/",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_profile(
    profile: ProfileCreate,
    db=Depends(get_db),
):
    try:
        response = await (
            db.table("profiles")
            .insert(profile.model_dump())
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create profile",
            )

        return response.data[0]

    except HTTPException:
        raise
    except APIError as e:
        if "duplicate key" in str(e).lower():
            raise HTTPException(status_code=409, detail={
                "code": "EMAIL_EXISTS",
                "message": "A profile with this email already exists"
            })
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating profile: {str(e)}")