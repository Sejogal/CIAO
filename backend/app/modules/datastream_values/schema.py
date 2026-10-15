from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DatastreamValueCreate(BaseModel):
    value: Any
    recorded_at: datetime | None = None


class DatastreamValueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    datastream_id: UUID
    value: Any
    recorded_at: datetime
