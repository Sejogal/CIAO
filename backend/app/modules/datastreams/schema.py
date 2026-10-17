from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from typing import Literal


DatastreamType = Literal["boolean", "integer", "float", "string", "json"]


class DatastreamCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    key: str = Field(..., min_length=1, max_length=100)
    data_type: DatastreamType
    unit: str | None = Field(default=None, max_length=30)
    min_value: float | None = None
    max_value: float | None = None


class DatastreamUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    key: str | None = Field(default=None, min_length=1, max_length=100)
    data_type: DatastreamType | None = None
    unit: str | None = Field(default=None, max_length=30)
    min_value: float | None = None
    max_value: float | None = None
    is_active: bool | None = None


class DatastreamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    device_id: UUID
    name: str
    key: str
    data_type: DatastreamType
    unit: str | None
    min_value: float | None
    max_value: float | None
    is_active: bool
