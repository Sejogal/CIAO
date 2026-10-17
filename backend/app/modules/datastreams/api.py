from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.datastreams.schema import (
    DatastreamCreate,
    DatastreamResponse,
    DatastreamUpdate,
)
from app.modules.datastreams.service import DatastreamService
from app.modules.identity.dependencies import get_current_user, require_permission
from app.modules.identity.model import User


router = APIRouter(tags=["Datastreams"])


@router.post(
    "/devices/{device_id}",
    response_model=DatastreamResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("datastreams:create"))],
)
async def create_datastream(
    device_id: UUID,
    data: DatastreamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await DatastreamService.create(
        db=db,
        user_id=current_user.id,
        device_id=device_id,
        data=data,
    )


@router.get(
    "/devices/{device_id}",
    response_model=list[DatastreamResponse],
)
async def list_device_datastreams(
    device_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("datastreams:read")),
):
    return await DatastreamService.list_by_device(
        db=db,
        device_id=device_id,
        user_id=current_user.id,
    )


@router.get(
    "/{datastream_id}",
    response_model=DatastreamResponse,
)
async def get_datastream(
    datastream_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("datastreams:read")),
):
    return await DatastreamService.get_for_user(
        db=db,
        datastream_id=datastream_id,
        user_id=current_user.id,
    )


@router.patch(
    "/{datastream_id}",
    response_model=DatastreamResponse,
    status_code=status.HTTP_200_OK,
)
async def update_datastream(
    datastream_id: UUID,
    data: DatastreamUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("datastreams:update")),
):
    return await DatastreamService.update(
        db=db,
        datastream_id=datastream_id,
        user_id=current_user.id,
        data=data,
    )


@router.delete(
    "/{datastream_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_datastream(
    datastream_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("datastreams:delete")),
):
    await DatastreamService.delete(
        db=db,
        datastream_id=datastream_id,
        user_id=current_user.id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
