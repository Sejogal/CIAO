from fastapi import FastAPI

from app.modules.identity.api import router as identity_router

app = FastAPI(
    title="CIAO API",
    version="1.0.0",
)

app.include_router(
    identity_router,
    prefix="/api/v1/identity",
    tags=["Identity"],
)


@app.get("/")
async def root():
    return {
        "project": "Conecta IoT Angola - CIAO",
        "status": "running",
        "CEO":"Seth Lussueki",
    }