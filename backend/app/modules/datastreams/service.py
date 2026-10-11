from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.datastreams.model import Datastream
from app.modules.datastreams.repository import DatastreamRepository
from app.modules.datastreams.schema import (
    DatastreamCreate,
    DatastreamUpdate,
)
from app.modules.devices.service import DeviceService


class DatastreamService:

    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: UUID,
        device_id: UUID,
        data: DatastreamCreate,
    ) -> Datastream:

        device = await DeviceService.get_for_user(
            db=db,
            device_id=device_id,
            user_id=user_id,
        )

        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Device not found",
            )

        existing = await DatastreamRepository.get_by_key(
            db=db,
            device_id=device_id,
            key=data.key,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Datastream key already exists for this device",
            )

        if (
            data.min_value is not None
            and data.max_value is not None
            and data.min_value > data.max_value
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="min_value cannot be greater than max_value",
            )

        datastream = Datastream(
            device_id=device_id,
            name=data.name,
            key=data.key,
            data_type=data.data_type,
            unit=data.unit,
            min_value=data.min_value,
            max_value=data.max_value,
            is_active=True,
        )

        return await DatastreamRepository.create(
            db=db,
            datastream=datastream,
        )

    @staticmethod
    async def list_by_device(
        db: AsyncSession,
        device_id: UUID,
        user_id: UUID,
    ) -> list[Datastream]:

        await DeviceService.get_for_user(
            db=db,
            device_id=device_id,
            user_id=user_id,
        )

        return await DatastreamRepository.get_by_device(
            db=db,
            device_id=device_id,
        )

    @staticmethod
    async def get_for_user(
        db: AsyncSession,
        datastream_id: UUID,
        user_id: UUID,
    ) -> Datastream:

        datastream = await DatastreamRepository.get_by_id(
            db=db,
            datastream_id=datastream_id,
        )

        if not datastream:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Datastream not found",
            )

        await DeviceService.get_for_user(
            db=db,
            device_id=datastream.device_id,
            user_id=user_id,
        )

        return datastream

    @staticmethod
    async def update(
        db: AsyncSession,
        datastream_id: UUID,
        user_id: UUID,
        data: DatastreamUpdate,
    ) -> Datastream:

        datastream = await DatastreamService.get_for_user(
            db=db,
            datastream_id=datastream_id,
            user_id=user_id,
        )

        update_data = data.model_dump(exclude_unset=True)

        if "key" in update_data:
            existing = await DatastreamRepository.get_by_key(
                db=db,
                device_id=datastream.device_id,
                key=update_data["key"],
            )

            if existing and existing.id != datastream.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Datastream key already exists for this device",
                )

        min_value = update_data.get(
            "min_value",
            datastream.min_value,
        )

        max_value = update_data.get(
            "max_value",
            datastream.max_value,
        )

        if (
            min_value is not None
            and max_value is not None
            and min_value > max_value
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="min_value cannot be greater than max_value",
            )

        if update_data:
            datastream = await DatastreamRepository.update(
                db=db,
                datastream=datastream,
                data=update_data,
            )

        return datastream

    @staticmethod
    async def delete(
        db: AsyncSession,
        datastream_id: UUID,
        user_id: UUID,
    ) -> None:

        datastream = await DatastreamService.get_for_user(
            db=db,
            datastream_id=datastream_id,
            user_id=user_id,
        )

        await DatastreamRepository.delete(
            db=db,
            datastream=datastream,
        )