from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.datastream_values.model import DatastreamValue
from app.modules.datastream_values.repository import DatastreamValueRepository
from app.modules.datastream_values.schema import DatastreamValueCreate
from app.modules.datastreams.service import DatastreamService
from app.modules.automation.service import AutomationService
from app.modules.devices.service import DeviceService

SUPPORTED_DATA_TYPES = {"boolean", "integer", "float", "string", "json"}


def value_matches_data_type(value, data_type: str) -> bool:
    if data_type == "boolean":
        return isinstance(value, bool)
    if data_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if data_type == "float":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if data_type == "string":
        return isinstance(value, str)
    if data_type == "json":
        return True
    # Datastream.data_type is constrained by the request schema and DB.
    return False


def _validate_value_matches_data_type(value, data_type: str) -> None:
    if not value_matches_data_type(value, data_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Value does not match this datastream's data_type "
                f"('{data_type}')"
            ),
        )


class DatastreamValueService:

    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: UUID,
        datastream_id: UUID,
        data: DatastreamValueCreate,
    ) -> DatastreamValue:

        datastream = await DatastreamService.get_for_user(
            db=db,
            datastream_id=datastream_id,
            user_id=user_id,
        )

        device = await DeviceService.get_for_user(
            db=db,
            device_id=datastream.device_id,
            user_id=user_id,
        )
        await DeviceService.require_project_owner(
            db=db,
            project_id=device.project_id,
            user_id=user_id,
        )

        _validate_value_matches_data_type(
            data.value,
            datastream.data_type,
        )

        value = DatastreamValue(
            datastream_id=datastream_id,
            value=data.value,
            recorded_at=data.recorded_at or datetime.now(timezone.utc),
        )

        created = await DatastreamValueRepository.create(
            db=db,
            value=value,
        )
        await AutomationService.evaluate(
            db=db,
            datastream_id=datastream_id,
            value=data.value,
        )
        return created

    @staticmethod
    async def get_latest(
        db: AsyncSession,
        user_id: UUID,
        datastream_id: UUID,
    ) -> DatastreamValue:

        await DatastreamService.get_for_user(
            db=db,
            datastream_id=datastream_id,
            user_id=user_id,
        )

        latest = await DatastreamValueRepository.get_latest(
            db=db,
            datastream_id=datastream_id,
        )

        if not latest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This datastream has no recorded values yet",
            )

        return latest

    @staticmethod
    async def list_history(
        db: AsyncSession,
        user_id: UUID,
        datastream_id: UUID,
        since: datetime | None,
        until: datetime | None,
        limit: int,
        offset: int,
    ) -> list[DatastreamValue]:

        await DatastreamService.get_for_user(
            db=db,
            datastream_id=datastream_id,
            user_id=user_id,
        )

        return await DatastreamValueRepository.list_by_datastream(
            db=db,
            datastream_id=datastream_id,
            since=since,
            until=until,
            limit=limit,
            offset=offset,
        )
