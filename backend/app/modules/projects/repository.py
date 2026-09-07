from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.projects.model import Project


class ProjectRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        project: Project,
    ) -> Project:

        db.add(project)

        await db.commit()
        await db.refresh(project)

        return project

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        project_id: UUID,
    ) -> Project | None:

        stmt = select(Project).where(
            Project.id == project_id
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_owner(
        db: AsyncSession,
        owner_id: UUID,
    ) -> list[Project]:

        stmt = (
            select(Project)
            .where(Project.owner_id == owner_id)
            .order_by(Project.created_at.desc())
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())

    @staticmethod
    async def delete(
        db: AsyncSession,
        project: Project,
    ) -> None:

        await db.delete(project)

        await db.commit()