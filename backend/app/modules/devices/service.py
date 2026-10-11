from secrets import token_urlsafe
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.devices.model import Device
from app.modules.devices.repository import DeviceRepository
from app.modules.devices.schema import DeviceCreate, DeviceUpdate
from app.modules.projects.service import ProjectService


class DeviceService:

    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: UUID,
        project_id: UUID,
        data: DeviceCreate,
    ) -> Device:

        # Verifica se o utilizador tem acesso ao projeto
        project = await ProjectService.get_for_user(
            db=db,
            project_id=project_id,
            user_id=user_id,
        )

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        device = Device(
            project_id=project_id,
            uuid=str(uuid4()),
            token=token_urlsafe(32),
            name=data.name,
            serial=data.serial,
            model=data.model,
            firmware_version=data.firmware_version,
            status="offline",
            is_active=True,
        )

        return await DeviceRepository.create(
            db=db,
            device=device,
        )

    @staticmethod
    async def list_by_project(
        db: AsyncSession,
        project_id: UUID,
        user_id: UUID,
    ) -> list[Device]:

        # Verifica acesso ao projeto
        await ProjectService.get_for_user(
            db=db,
            project_id=project_id,
            user_id=user_id,
        )

        return await DeviceRepository.get_by_project(
            db=db,
            project_id=project_id,
        )

    @staticmethod
    async def get_for_user(
        db: AsyncSession,
        device_id: UUID,
        user_id: UUID,
    ) -> Device:

        device = await DeviceRepository.get_by_id(
            db=db,
            device_id=device_id,
        )

        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found",
            )

        # Verifica se o utilizador tem acesso ao projeto
        await ProjectService.get_for_user(
            db=db,
            project_id=device.project_id,
            user_id=user_id,
        )

        return device

    @staticmethod
    async def update(
        db: AsyncSession,
        device_id: UUID,
        user_id: UUID,
        data: DeviceUpdate,
    ) -> Device:

        device = await DeviceService.get_for_user(
            db=db,
            device_id=device_id,
            user_id=user_id,
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        if update_data:
            device = await DeviceRepository.update(
                db=db,
                device=device,
                data=update_data,
            )

        return device

    @staticmethod
    async def delete(
        db: AsyncSession,
        device_id: UUID,
        user_id: UUID,
    ) -> None:

        device = await DeviceService.get_for_user(
            db=db,
            device_id=device_id,
            user_id=user_id,
        )

        await DeviceRepository.delete(
            db=db,
            device=device,
        )