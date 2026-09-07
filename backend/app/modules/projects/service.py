from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.projects.model import Project
from app.modules.projects.repository import ProjectRepository
from app.modules.projects.schema import (
    ProjectCreate,
    ProjectUpdate,
)


class ProjectService:

    @staticmethod
    async def create(
        db: AsyncSession,
        owner_id: UUID,
        data: ProjectCreate,
    ) -> Project:

        project = Project(
            name=data.name,
            description=data.description,
            owner_id=owner_id,
        )

        return await ProjectRepository.create(
            db,
            project,
        )

    @staticmethod
    async def list(
        db: AsyncSession,
        owner_id: UUID,
    ) -> list[Project]:

        return await ProjectRepository.get_by_owner(
            db,
            owner_id,
        )

    @staticmethod
    async def get(
        db: AsyncSession,
        project_id: UUID,
        owner_id: UUID,
    ) -> Project:

        project = await ProjectRepository.get_by_id(
            db,
            project_id,
        )

        if not project or project.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        return project

    @staticmethod
    async def update(
        db: AsyncSession,
        project_id: UUID,
        owner_id: UUID,
        data: ProjectUpdate,
    ) -> Project:

        project = await ProjectRepository.get_by_id(
            db,
            project_id,
        )

        if not project or project.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        if data.name is not None:
            project.name = data.name

        if data.description is not None:
            project.description = data.description

        await db.commit()
        await db.refresh(project)

        return project

    @staticmethod
    async def delete(
        db: AsyncSession,
        project_id: UUID,
        owner_id: UUID,
    ) -> None:

        project = await ProjectRepository.get_by_id(
            db,
            project_id,
        )

        if not project or project.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        await ProjectRepository.delete(
            db,
            project,
        )