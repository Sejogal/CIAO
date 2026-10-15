from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.datastream_values.model import DatastreamValue


class DatastreamValueRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        value: DatastreamValue,
    ) -> DatastreamValue:
        db.add(value)
        await db.flush()
        await db.refresh(value)
        return value

    @staticmethod
    async def get_latest(
        db: AsyncSession,
        datastream_id: UUID,
    ) -> DatastreamValue | None:
        stmt = (
            select(DatastreamValue)
            .where(DatastreamValue.datastream_id == datastream_id)
            .order_by(DatastreamValue.recorded_at.desc())
            .limit(1)
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_datastream(
        db: AsyncSession,
        datastream_id: UUID,
        since: datetime | None,
        until: datetime | None,
        limit: int,
        offset: int,
    ) -> list[DatastreamValue]:
        stmt = select(DatastreamValue).where(
            DatastreamValue.datastream_id == datastream_id
        )

        if since is not None:
            stmt = stmt.where(DatastreamValue.recorded_at >= since)

        if until is not None:
            stmt = stmt.where(DatastreamValue.recorded_at <= until)

        stmt = (
            stmt.order_by(DatastreamValue.recorded_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())
