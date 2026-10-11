from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.projects.model import Project
from app.modules.companies.model import Company, CompanyMember



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

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        project_id: UUID,
    ) -> Project | None:
        stmt = select(Project).where(Project.id == project_id)

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    async def get_for_user(
        db: AsyncSession,
        user_id: UUID,
    ) -> list[Project]:

        stmt = (
            select(Project)
            .outerjoin(
                CompanyMember,
                CompanyMember.company_id == Project.company_id,
            )
            .where(
                (Project.owner_id == user_id)
                | (CompanyMember.user_id == user_id)
            )
            .distinct()
            .order_by(Project.created_at.desc())
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())

    @staticmethod
    async def get_for_user_by_id(
        db: AsyncSession,
        project_id: UUID,
        user_id: UUID,
    ) -> Project | None:

        stmt = (
            select(Project)
            .outerjoin(
                CompanyMember,
                CompanyMember.company_id == Project.company_id,
            )
            .where(
                Project.id == project_id,
                (
                    (Project.owner_id == user_id)
                    | (CompanyMember.user_id == user_id)
                ),
            )
            .distinct()
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()


    @staticmethod
    async def update(
        db: AsyncSession,
        project: Project,
        data: dict,
    ) -> Project:
        for field, value in data.items():
            setattr(project, field, value)

        await db.flush()
        await db.refresh(project)

        return project


    @staticmethod
    async def delete(
        db: AsyncSession,
        project: Project,
    ) -> None:
        await db.delete(project)
        await db.flush()