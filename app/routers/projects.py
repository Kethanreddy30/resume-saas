from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from postgrest.exceptions import APIError

from app.database import get_db
from app.dependencies.auth import require_user_id
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


async def _get_project_or_404(db, project_id: str) -> dict:
    response = await db.table("projects").select("*").eq("id", project_id).execute()
    if not response.data:
        raise HTTPException(
            status_code=404,
            detail={"code": "PROJECT_NOT_FOUND", "message": "Project not found"},
        )
    return response.data[0]


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    db=Depends(get_db),
):
    try:
        payload = project.model_dump()
        payload["profile_id"] = str(payload["profile_id"])
        response = await db.table("projects").insert(payload).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create project")
        return response.data[0]
    except HTTPException:
        raise
    except APIError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db=Depends(get_db),
):
    return await _get_project_or_404(db, project_id)


@router.get("/profile/{profile_id}", response_model=List[ProjectResponse])
async def list_profile_projects(
    profile_id: str,
    db=Depends(get_db),
):
    response = await (
        db.table("projects")
        .select("*")
        .eq("profile_id", profile_id)
        .order("order_index")
        .execute()
    )
    return response.data


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    db=Depends(get_db),
):
    await _get_project_or_404(db, project_id)
    update_data = project_update.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    await db.table("projects").update(update_data).eq("id", project_id).execute()
    updated = await db.table("projects").select("*").eq("id", project_id).execute()
    return updated.data[0]


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db=Depends(get_db),
):
    await _get_project_or_404(db, project_id)
    await db.table("projects").delete().eq("id", project_id).execute()