from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.companies.model import Company, CompanyMember
from app.modules.companies.repository import CompanyRepository
from app.modules.companies.schemas import (
    CompanyCreate,
    CompanyMemberCreate,
    CompanyMemberUpdate,
    CompanyUpdate,
)
from app.modules.companies.utils import slugify
from app.modules.identity.model import User


class CompanyService:

    @staticmethod
    async def create(
        db: AsyncSession,
        owner_id: UUID,
        data: CompanyCreate,
    ) -> Company:

        slug = slugify(data.name)

        existing = await CompanyRepository.get_by_slug(
            db,
            slug,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Company slug already exists",
            )

        company = Company(
            name=data.name,
            slug=slug,
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
        requester_id: UUID,
        data: CompanyMemberCreate,
    ) -> CompanyMember:

        # Verifica se a empresa existe
        await CompanyService.get(
            db,
            company_id,
        )

        # Obtém o membro que está fazendo a requisição
        requester = await CompanyService.get_member_or_403(
            db,
            company_id,
            requester_id,
        )

        # Apenas owner e admin podem adicionar membros
        if requester.role not in ("owner", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to add members",
            )

        # Verifica se o utilizador existe
        user = await db.get(
            User,
            data.user_id,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Verifica se já é membro
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

        # Não permitir criar outro owner
        if data.role == "owner":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot add another owner",
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


    @staticmethod
    async def get_member_or_403(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
    ) -> CompanyMember:

        member = await CompanyRepository.get_member(
            db,
            company_id,
            user_id,
        )

        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this company",
            )

        return member


    @staticmethod
    async def list_members(
        db: AsyncSession,
        company_id: UUID,
        requester_id: UUID,
    ) -> list[CompanyMember]:

        # Verifica se a empresa existe
        await CompanyService.get(
            db,
            company_id,
        )

        # Verifica se o utilizador pertence à empresa
        await CompanyService.get_member_or_403(
            db,
            company_id,
            requester_id,
        )

        return await CompanyRepository.get_members(
            db,
            company_id,
        )
    

    @staticmethod
    async def update_member(
        db: AsyncSession,
        company_id: UUID,
        requester_id: UUID,
        user_id: UUID,
        data: CompanyMemberUpdate,
    ) -> CompanyMember:

        requester = await CompanyService.get_member_or_403(
            db,
            company_id,
            requester_id,
        )

        # Apenas owner e admin podem alterar membros
        if requester.role not in ("owner", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update members",
            )

        member = await CompanyRepository.get_member(
            db,
            company_id,
            user_id,
        )

        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company member not found",
            )

        # Owner não pode ser alterado
        if member.role == "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify the company owner",
            )

        # Não permitir promover alguém para owner
        if data.role == "owner":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign owner role",
            )

        return await CompanyRepository.update_member_role(
            db,
            member,
            data.role,
        )


    @staticmethod
    async def remove_member(
        db: AsyncSession,
        company_id: UUID,
        requester_id: UUID,
        user_id: UUID,
    ) -> None:

        requester = await CompanyService.get_member_or_403(
            db,
            company_id,
            requester_id,
        )

        # Apenas owner e admin
        if requester.role not in ("owner", "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to remove members",
            )

        member = await CompanyRepository.get_member(
            db,
            company_id,
            user_id,
        )

        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company member not found",
            )

        # Owner nunca pode ser removido
        if member.role == "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot remove the company owner",
            )

        await CompanyRepository.remove_member(
            db,
            member,
        )


    @staticmethod
    async def get_for_user(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
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

        # Owner também é considerado membro
        if company.owner_id == user_id:
            return company

        member = await CompanyRepository.get_member(
            db,
            company_id,
            user_id,
        )

        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a member of this company",
            )

        return company
    

    @staticmethod
    async def list_for_user(
        db: AsyncSession,
        user_id: UUID,
    ) -> list[Company]:

        return await CompanyRepository.get_for_user(
            db,
            user_id,
        )
