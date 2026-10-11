from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.datastreams.model import Datastream


class DatastreamRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        datastream: Datastream,
    ) -> Datastream:
        db.add(datastream)
        await db.flush()
        await db.refresh(datastream)
        return datastream

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        datastream_id: UUID,
    ) -> Datastream | None:
        stmt = select(Datastream).where(
            Datastream.id == datastream_id
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_key(
        db: AsyncSession,
        device_id: UUID,
        key: str,
    ) -> Datastream | None:
        stmt = select(Datastream).where(
            Datastream.device_id == device_id,
            Datastream.key == key,
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_device(
        db: AsyncSession,
        device_id: UUID,
    ) -> list[Datastream]:
        stmt = (
            select(Datastream)
            .where(Datastream.device_id == device_id)
            .order_by(Datastream.created_at.desc())
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())

    @staticmethod
    async def update(
        db: AsyncSession,
        datastream: Datastream,
        data: dict,
    ) -> Datastream:

        for field, value in data.items():
            setattr(datastream, field, value)

        await db.flush()
        await db.refresh(datastream)

        return datastream

    @staticmethod
    async def delete(
        db: AsyncSession,
        datastream: Datastream,
    ) -> None:

        await db.delete(datastream)
        await db.flush()