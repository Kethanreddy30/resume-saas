from fastapi import APIRouter, Depends, HTTPException
from postgrest.exceptions import APIError
from app.database import get_db

router = APIRouter(prefix="/api/v1/portfolio", tags=["portfolio"])


@router.get("/{profile_id}")
async def get_portfolio(
    profile_id: str,
    db=Depends(get_db),
):
    try:
        # Fetch profile
        profile_res = await (
            db.table("profiles")
            .select("*")
            .eq("id", profile_id)
            .execute()
        )
        if not profile_res.data:
            raise HTTPException(
                status_code=404,
                detail={"code": "PROFILE_NOT_FOUND", "message": "Profile not found"},
            )
        profile = profile_res.data[0]

        # Fetch projects
        projects_res = await (
            db.table("projects")
            .select("*")
            .eq("profile_id", profile_id)
            .order("order_index")
            .execute()
        )
        projects = projects_res.data

        return {
            "profile": {
                "id": profile.get("id"),
                "full_name": profile.get("full_name"),
                "email": profile.get("email"),
                "role": profile.get("role"),
                "tagline": profile.get("tagline"),
                "summary": profile.get("summary"),
                "location": profile.get("location"),
                "github_url": profile.get("github_url"),
                "linkedin_url": profile.get("linkedin_url"),
                "open_to": profile.get("open_to", []),
                "skills": profile.get("skills", []),
                "experience": profile.get("experience", []),
                "education": profile.get("education", []),
                "philosophy": profile.get("philosophy", []),
                "timeline": profile.get("timeline", []),
                "debug_stories": profile.get("debug_stories", []),
            },
            "projects": projects,
        }

    except HTTPException:
        raise
    except APIError as e:
        raise HTTPException(
            status_code=500,
            detail={"code": "DB_ERROR", "message": str(e)[:200]},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": "INTERNAL_ERROR", "message": str(e)[:200]},
        )