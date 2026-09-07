from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.companies.model import Company, CompanyMember
from app.modules.companies.repository import CompanyRepository
from app.modules.companies.schema import (
    CompanyCreate,
    CompanyMemberCreate,
    CompanyUpdate,
)


class CompanyService:

    @staticmethod
    async def create(
        db: AsyncSession,
        owner_id: UUID,
        data: CompanyCreate,
    ) -> Company:

        existing = await CompanyRepository.get_by_slug(
            db,
            data.slug,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Company slug already exists",
            )

        company = Company(
            name=data.name,
            slug=data.slug,
            description=data.description,
            owner_id=owner_id,
        )

        company = await CompanyRepository.create(
            db,
            company,
        )

        # O proprietário também vira membro.
        member = CompanyMember(
            company_id=company.id,
            user_id=owner_id,
            role="owner",
        )

        await CompanyRepository.add_member(
            db,
            member,
        )

        return company

    @staticmethod
    async def get(
        db: AsyncSession,
        company_id: UUID,
    ) -> Company:

        company = await CompanyRepository.get_by_id(
            db,
            company_id,
        )

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found",
            )

        return company

    @staticmethod
    async def list_mine(
        db: AsyncSession,
        owner_id: UUID,
    ) -> list[Company]:

        return await CompanyRepository.get_by_owner(
            db,
            owner_id,
        )

    @staticmethod
    async def update(
        db: AsyncSession,
        company_id: UUID,
        owner_id: UUID,
        data: CompanyUpdate,
    ) -> Company:

        company = await CompanyService.get(
            db,
            company_id,
        )

        if company.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the company owner can update it",
            )

        if data.name is not None:
            company.name = data.name

        if data.description is not None:
            company.description = data.description

        await db.commit()
        await db.refresh(company)

        return company

    @staticmethod
    async def add_member(
        db: AsyncSession,
        company_id: UUID,
        owner_id: UUID,
        data: CompanyMemberCreate,
    ) -> CompanyMember:

        company = await CompanyService.get(
            db,
            company_id,
        )

        if company.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the company owner can add members",
            )

        existing = await CompanyRepository.get_member(
            db,
            company_id,
            data.user_id,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already a company member",
            )

        member = CompanyMember(
            company_id=company_id,
            user_id=data.user_id,
            role=data.role,
        )

        return await CompanyRepository.add_member(
            db,
            member,
        )