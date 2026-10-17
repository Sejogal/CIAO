from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.datastream_values.schema import (
    DatastreamValueCreate,
    DatastreamValueResponse,
)
from app.modules.datastream_values.service import DatastreamValueService
from app.modules.identity.dependencies import get_current_user, require_permission
from app.modules.identity.model import User

router = APIRouter(tags=["Datastream Values"])


@router.post(
    "/{datastream_id}/values",
    response_model=DatastreamValueResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("datastreams:update"))],
)
async def create_datastream_value(
    datastream_id: UUID,
    data: DatastreamValueCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await DatastreamValueService.create(
        db=db,
        user_id=current_user.id,
        datastream_id=datastream_id,
        data=data,
    )


@router.get(
    "/{datastream_id}/values/latest",
    response_model=DatastreamValueResponse,
)
async def get_latest_datastream_value(
    datastream_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("datastreams:read")),
):
    return await DatastreamValueService.get_latest(
        db=db,
        user_id=current_user.id,
        datastream_id=datastream_id,
    )


@router.get(
    "/{datastream_id}/values",
    response_model=list[DatastreamValueResponse],
)
async def list_datastream_values(
    datastream_id: UUID,
    since: datetime | None = Query(default=None),
    until: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("datastreams:read")),
):
    return await DatastreamValueService.list_history(
        db=db,
        user_id=current_user.id,
        datastream_id=datastream_id,
        since=since,
        until=until,
        limit=limit,
        offset=offset,
    )
