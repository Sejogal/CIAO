from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


DeviceStatus = Literal["online", "offline"]


class DeviceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)

    serial: str | None = Field(
        default=None,
        max_length=100,
    )

    model: str | None = Field(
        default=None,
        max_length=100,
    )

    firmware_version: str | None = Field(
        default=None,
        max_length=50,
    )


class DeviceUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    serial: str | None = Field(
        default=None,
        max_length=100,
    )

    model: str | None = Field(
        default=None,
        max_length=100,
    )

    firmware_version: str | None = Field(
        default=None,
        max_length=50,
    )

    is_active: bool | None = None


class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    uuid: str
    serial: str | None
    name: str
    model: str | None
    firmware_version: str | None
    status: DeviceStatus
    last_seen: datetime | None
    is_active: bool


class DeviceCreateResponse(DeviceResponse):
    """
    Only ever returned from the create endpoint. `token` and
    `mqtt_password` are shown here once, in plaintext, and never again -
    the DB only keeps `mqtt_password`'s hash. Lose them and the device
    must be re-provisioned (new credentials, same device row).
    """

    token: str
    mqtt_username: str
    mqtt_password: str
