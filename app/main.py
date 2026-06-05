from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.health import router as health_router
from app.routers.jobs import router as jobs_router
from app.routers.profiles import router as profiles_router
from app.routers.tailor import router as tailor_router
from app.routers.uploads import router as uploads_router
from app.routers.projects import router as projects_router
from app.routers.portfolio import router as portfolio_router

app = FastAPI(title="Resume SaaS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(profiles_router)
app.include_router(uploads_router)
app.include_router(jobs_router)
app.include_router(tailor_router)
app.include_router(projects_router)
app.include_router(portfolio_router)
