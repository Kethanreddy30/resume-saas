from fastapi import FastAPI

from app.routers.health import router as health_router
from app.routers.profiles import router as profiles_router

app = FastAPI()

app.include_router(health_router)
app.include_router(profiles_router)