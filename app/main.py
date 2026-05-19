from fastapi import FastAPI
from app.routers.health import router as health_router
from app.routers.profiles import router as profiles_router
from app.routers.uploads import router as uploads_router

app = FastAPI(title="Resume SaaS API")

app.include_router(health_router)
app.include_router(profiles_router)
app.include_router(uploads_router)