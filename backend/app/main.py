import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.identity.api import router as identity_router
from app.modules.projects.api import router as projects_router
from app.modules.companies.api import router as companies_router
from app.modules.devices.api import router as devices_router
from app.modules.datastreams.api import router as datastreams_router
from app.modules.datastream_values.api import router as datastream_values_router
from app.modules.dashboards.api import router as dashboards_router
from app.modules.automation.api import automation_router, notification_router
from app.modules.mqtt.commands import run_command_publish_loop
from app.modules.mqtt.client import run_mqtt_ingest_loop
from app.modules.mqtt.heartbeat import run_device_heartbeat_loop
from app.modules.mqtt.auth import router as mqtt_auth_router
from app.db import models

logger = logging.getLogger("ciao.mqtt")


@asynccontextmanager
async def lifespan(_: FastAPI):
    mqtt_task = asyncio.create_task(run_mqtt_ingest_loop())
    command_task = asyncio.create_task(run_command_publish_loop())
    heartbeat_task = asyncio.create_task(run_device_heartbeat_loop())

    yield

    mqtt_task.cancel()
    command_task.cancel()
    heartbeat_task.cancel()
    try:
        await asyncio.gather(mqtt_task, command_task, heartbeat_task)
    except asyncio.CancelledError:
        pass
    except Exception:
        logger.exception("mqtt: ingest loop raised on shutdown")


app = FastAPI(
    title="CIAO API",
    version="1.0.0",
    lifespan=lifespan,
)

# Dev only: o app Expo corre em origens variáveis (web local, túneis, etc.)
# e ainda não há domínio de produção fixo para restringir isto.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
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

app.include_router(
    dashboards_router,
    prefix="/api/v1/dashboards",
    tags=["Dashboards and Widgets"],
)

app.include_router(automation_router, prefix="/api/v1/automations", tags=["Automations"])
app.include_router(notification_router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(mqtt_auth_router, prefix="/api/v1/mqtt", tags=["MQTT Broker"])


@app.get("/")
async def root():
    return {
        "project": "Conecta IoT Angola - CIAO",
        "status": "running",
        "CEO":"Seth Lussueki",
    }
