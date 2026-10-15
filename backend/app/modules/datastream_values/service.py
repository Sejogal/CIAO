from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.datastream_values.model import DatastreamValue
from app.modules.datastream_values.repository import DatastreamValueRepository
from app.modules.datastream_values.schema import DatastreamValueCreate
from app.modules.datastreams.service import DatastreamService

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
    # Datastream.data_type is free-text (no DB-level enum yet - see
    # README_CIAO.md Prioridade 3); anything outside the known set is
    # treated as opaque JSON rather than rejected.
    return True


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

        _validate_value_matches_data_type(
            data.value,
            datastream.data_type,
        )

        value = DatastreamValue(
            datastream_id=datastream_id,
            value=data.value,
            recorded_at=data.recorded_at or datetime.now(),
        )

        return await DatastreamValueRepository.create(
            db=db,
            value=value,
        )

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
