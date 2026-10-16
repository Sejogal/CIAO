from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AutomationCreate(BaseModel):
    project_id: UUID
    datastream_id: UUID
    name: str = Field(min_length=1, max_length=150)
    operator: str = Field(pattern="^(<|>|=)$")
    threshold: float
    action: str = Field(default="Enviar notificação", min_length=1, max_length=2000)
    action_type: Literal["notification", "control_device"] = "notification"
    target_datastream_id: UUID | None = None
    action_value: Any | None = None
    is_active: bool = True
    cooldown_seconds: int = Field(default=300, ge=0, le=86400)


class AutomationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    operator: str | None = Field(default=None, pattern="^(<|>|=)$")
    threshold: float | None = None
    action: str | None = Field(default=None, min_length=1, max_length=2000)
    action_type: Literal["notification", "control_device"] | None = None
    target_datastream_id: UUID | None = None
    action_value: Any | None = None
    is_active: bool | None = None
    cooldown_seconds: int | None = Field(default=None, ge=0, le=86400)


class AutomationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    datastream_id: UUID
    owner_id: UUID
    name: str
    operator: str
    threshold: float
    action: str
    action_type: str
    target_datastream_id: UUID | None
    action_value: Any | None
    is_active: bool
    cooldown_seconds: int
    last_triggered_at: datetime | None
    created_at: datetime
    updated_at: datetime


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    user_id: UUID
    project_id: UUID
    automation_id: UUID | None
    datastream_id: UUID | None
    title: str
    message: str
    level: str
    read_at: datetime | None
    created_at: datetime


class NotificationReadUpdate(BaseModel):
    read: bool = True
