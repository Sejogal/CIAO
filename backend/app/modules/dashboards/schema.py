from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DashboardCreate(BaseModel):
    project_id: UUID
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    layout: dict[str, Any] = Field(default_factory=dict)


class DashboardUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    layout: dict[str, Any] | None = None


class DashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    project_id: UUID
    owner_id: UUID
    name: str
    description: str | None
    layout: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class WidgetCreate(BaseModel):
    datastream_id: UUID
    name: str = Field(min_length=1, max_length=150)
    widget_type: str = Field(min_length=1, max_length=40)
    config: dict[str, Any] = Field(default_factory=dict)
    position: dict[str, Any] = Field(default_factory=dict)


class WidgetUpdate(BaseModel):
    datastream_id: UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=150)
    widget_type: str | None = Field(default=None, min_length=1, max_length=40)
    config: dict[str, Any] | None = None
    position: dict[str, Any] | None = None


class WidgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    dashboard_id: UUID
    datastream_id: UUID
    name: str
    widget_type: str
    config: dict[str, Any]
    position: dict[str, Any]
    created_at: datetime
    updated_at: datetime
