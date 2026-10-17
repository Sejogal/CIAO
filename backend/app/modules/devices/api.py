from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.devices.schema import (
    DeviceCreate,
    DeviceCreateResponse,
    DeviceResponse,
    DeviceUpdate,
)
from app.modules.devices.service import DeviceService
from app.modules.identity.dependencies import get_current_user, require_permission
from app.modules.identity.model import User


router = APIRouter(
    tags=["Devices"],
)


@router.post(
    "/projects/{project_id}",
    response_model=DeviceCreateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("devices:create"))],
)
async def create_device(
    project_id: UUID,
    data: DeviceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    device, token, mqtt_password = await DeviceService.create(
        db=db,
        user_id=current_user.id,
        project_id=project_id,
        data=data,
    )

    return DeviceCreateResponse(
        **DeviceResponse.model_validate(device).model_dump(),
        token=token,
        mqtt_username=device.mqtt_username,
        mqtt_password=mqtt_password,
    )


@router.get(
    "/projects/{project_id}",
    response_model=list[DeviceResponse],
)
async def list_project_devices(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("devices:read")),
):
    return await DeviceService.list_by_project(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )


@router.get(
    "/{device_id}",
    response_model=DeviceResponse,
)
async def get_device(
    device_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("devices:read")),
):
    return await DeviceService.get_for_user(
        db=db,
        device_id=device_id,
        user_id=current_user.id,
    )


@router.patch(
    "/{device_id}",
    response_model=DeviceResponse,
    status_code=status.HTTP_200_OK,
)
async def update_device(
    device_id: UUID,
    data: DeviceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("devices:update")),
):
    return await DeviceService.update(
        db=db,
        device_id=device_id,
        user_id=current_user.id,
        data=data,
    )


@router.post(
    "/{device_id}/credentials/rotate",
    response_model=DeviceCreateResponse,
    dependencies=[Depends(require_permission("devices:update"))],
)
async def rotate_device_credentials(
    device_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    device, token, mqtt_password = await DeviceService.rotate_credentials(
        db=db,
        device_id=device_id,
        user_id=current_user.id,
    )
    return DeviceCreateResponse(
        **DeviceResponse.model_validate(device).model_dump(),
        token=token,
        mqtt_username=device.mqtt_username,
        mqtt_password=mqtt_password,
    )


@router.delete(
    "/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_device(
    device_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("devices:delete")),
):
    await DeviceService.delete(
        db=db,
        device_id=device_id,
        user_id=current_user.id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
