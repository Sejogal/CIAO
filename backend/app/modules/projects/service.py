from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.projects.model import Project
from app.modules.projects.repository import ProjectRepository
from app.modules.projects.schema import (
    ProjectCreate,
    ProjectUpdate,
)
from app.modules.companies.repository import CompanyRepository
from app.modules.companies.model import Company, CompanyMember


class ProjectService:

    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: UUID,
        data: ProjectCreate,
    ) -> Project:

        company = await CompanyRepository.get_by_id(
            db,
            data.company_id,
        )

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found",
            )

        member = await CompanyRepository.get_member(
            db,
            data.company_id,
            user_id,
        )

        if not member and company.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this company",
            )

        project = Project(
            name=data.name,
            description=data.description,
            owner_id=user_id,
            company_id=data.company_id,
        )

        return await ProjectRepository.create(
            db,
            project,
        )


    @staticmethod
    async def list_for_user(
        db: AsyncSession,
        user_id: UUID,
    ) -> list[Project]:

        return await ProjectRepository.get_for_user(
            db=db,
            user_id=user_id,
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


    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        project_id: UUID,
    ) -> Project | None:
        stmt = select(Project).where(
            Project.id == project_id,
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    async def get_for_user(
        db: AsyncSession,
        project_id: UUID,
        user_id: UUID,
    ) -> Project:

        project = await ProjectRepository.get_for_user_by_id(
            db,
            project_id,
            user_id,
        )

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        return project

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
        project_id: UUID,
        user_id: UUID,
        data: ProjectUpdate,
    ) -> Project:

        project = await ProjectRepository.get_for_user_by_id(
            db=db,
            project_id=project_id,
            user_id=user_id,
        )

        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found",
            )

        # O dono do projeto pode editar
        if project.owner_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to update this project",
            )

        update_data = data.model_dump(exclude_unset=True)

        if update_data:
            project = await ProjectRepository.update(
                db=db,
                project=project,
                data=update_data,
            )

        return project



    @staticmethod
    async def delete(
        db: AsyncSession,
        project_id: UUID,
        user_id: UUID,
    ) -> None:

        project = await ProjectRepository.get_for_user_by_id(
            db=db,
            project_id=project_id,
            user_id=user_id,
        )

        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found",
            )

        if project.owner_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to delete this project",
            )

        await ProjectRepository.delete(
            db=db,
            project=project,
        )