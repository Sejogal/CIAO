import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.modules.identity.api import router as identity_router
from app.modules.projects.api import router as projects_router
from app.modules.companies.api import router as companies_router
from app.modules.devices.api import router as devices_router
from app.modules.datastreams.api import router as datastreams_router
from app.modules.datastream_values.api import router as datastream_values_router
from app.modules.mqtt.client import run_mqtt_ingest_loop
from app.db import models

logger = logging.getLogger("ciao.mqtt")


@asynccontextmanager
async def lifespan(_: FastAPI):
    mqtt_task = asyncio.create_task(run_mqtt_ingest_loop())

    yield

    mqtt_task.cancel()
    try:
        await mqtt_task
    except asyncio.CancelledError:
        pass
    except Exception:
        logger.exception("mqtt: ingest loop raised on shutdown")


app = FastAPI(
    title="CIAO API",
    version="1.0.0",
    lifespan=lifespan,
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

app.include_router(
    devices_router,
    prefix="/api/v1/devices",
    tags=["Devices"],
)

app.include_router(
    datastreams_router,
    prefix="/api/v1/datastreams",
    tags=["Datastreams"],
)

app.include_router(
    datastream_values_router,
    prefix="/api/v1/datastreams",
    tags=["Datastream Values"],
)


@app.get("/")
async def root():
    return {
        "project": "Conecta IoT Angola - CIAO",
        "status": "running",
        "CEO":"Seth Lussueki",
    }