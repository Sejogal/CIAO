from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.devices.model import Device


class DeviceRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        device: Device,
    ) -> Device:
        db.add(device)

        await db.flush()
        await db.refresh(device)

        return device

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        device_id: UUID,
    ) -> Device | None:
        stmt = select(Device).where(
            Device.id == device_id
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_uuid(
        db: AsyncSession,
        uuid: str,
    ) -> Device | None:
        stmt = select(Device).where(
            Device.uuid == uuid
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_project(
        db: AsyncSession,
        project_id: UUID,
    ) -> list[Device]:
        stmt = (
            select(Device)
            .where(Device.project_id == project_id)
            .order_by(Device.created_at.desc())
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())

    @staticmethod
    async def update(
        db: AsyncSession,
        device: Device,
        data: dict,
    ) -> Device:
        for field, value in data.items():
            setattr(device, field, value)

        await db.flush()
        await db.refresh(device)

        return device

    @staticmethod
    async def delete(
        db: AsyncSession,
        device: Device,
    ) -> None:
        await db.delete(device)

        await db.flush()