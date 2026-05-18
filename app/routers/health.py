from fastapi import APIRouter, Depends
from app.database import get_db
from datetime import datetime, timezone

router = APIRouter()

@router.get("/health")
async def health_check(db=Depends(get_db)):
    timestamp = datetime.now(timezone.utc).isoformat()
    try:
        await db.table("profiles").select("id").limit(1).execute()
        return {"status": "ok", "db": "ok", "timestamp": timestamp}
    except Exception:
        return {"status": "degraded", "db": "error", "timestamp": timestamp}