from fastapi import FastAPI

from app.modules.identity.api import router as identity_router
from app.modules.projects.api import router as projects_router
from app.modules.companies.api import router as companies_router
from app.db import models

app = FastAPI(
    title="CIAO API",
    version="1.0.0",
)

app.include_router(
    identity_router,
    prefix="/api/v1/identity",
    tags=["Identity"],
)

app.include_router(
    projects_router,
    prefix="/api/v1/projects",
    tags=["Projects"],
)

app.include_router(
    companies_router,
    prefix="/api/v1/companies",
    tags=["Companies"]
)


@app.get("/")
async def root():
    return {
        "project": "Conecta IoT Angola - CIAO",
        "status": "running",
        "CEO":"Seth Lussueki",
    }