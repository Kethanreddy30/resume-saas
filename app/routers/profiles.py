from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.schemas.profile import ProfileCreate, ProfileResponse

router = APIRouter(prefix="/api/v1/profiles", tags=["profiles"])


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

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating profile: {str(e)}",
        )