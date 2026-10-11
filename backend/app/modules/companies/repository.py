from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.companies.model import Company, CompanyMember


class CompanyRepository:

    @staticmethod
    async def create(
        db: AsyncSession,
        company: Company,
    ) -> Company:
        db.add(company)

        await db.commit()
        await db.refresh(company)

        return company

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        company_id: UUID,
    ) -> Company | None:

        stmt = select(Company).where(
            Company.id == company_id
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_slug(
        db: AsyncSession,
        slug: str,
    ) -> Company | None:

        stmt = select(Company).where(
            Company.slug == slug
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_owner(
        db: AsyncSession,
        owner_id: UUID,
    ) -> list[Company]:

        stmt = (
            select(Company)
            .where(Company.owner_id == owner_id)
            .order_by(Company.created_at.desc())
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())

    @staticmethod
    async def add_member(
        db: AsyncSession,
        member: CompanyMember,
    ) -> CompanyMember:

        db.add(member)

        await db.commit()
        await db.refresh(member)

        return member

    @staticmethod
    async def get_member(
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
    ) -> CompanyMember | None:

        stmt = select(CompanyMember).where(
            CompanyMember.company_id == company_id,
            CompanyMember.user_id == user_id,
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    
    @staticmethod
    async def get_members(
        db: AsyncSession,
        company_id: UUID,
    ) -> list[CompanyMember]:

        stmt = (
            select(CompanyMember)
            .where(
                CompanyMember.company_id == company_id
            )
            .options(
                selectinload(CompanyMember.user)
            )
            .order_by(CompanyMember.created_at.asc())
        )

        result = await db.execute(stmt)

        return list(
            result.scalars().all()
        )

    @staticmethod
    async def update_member_role(
        db: AsyncSession,
        member: CompanyMember,
        role: str,
    ) -> CompanyMember:

        member.role = role

        await db.commit()
        await db.refresh(member)

        return member

    @staticmethod
    async def remove_member(
        db: AsyncSession,
        member: CompanyMember,
    ) -> None:

        await db.delete(member)

        await db.commit()


    @staticmethod
    async def get_for_user(
        db: AsyncSession,
        user_id: UUID,
    ) -> list[Company]:

        stmt = (
            select(Company)
            .outerjoin(
                CompanyMember,
                CompanyMember.company_id == Company.id,
            )
            .where(
                (Company.owner_id == user_id)
                | (CompanyMember.user_id == user_id)
            )
            .distinct()
            .order_by(Company.created_at.desc())
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())
    

    @staticmethod
    async def get_for_user(
        db: AsyncSession,
        user_id: UUID,
    ) -> list[Company]:

        stmt = (
            select(Company)
            .outerjoin(
                CompanyMember,
                CompanyMember.company_id == Company.id,
            )
            .where(
                (Company.owner_id == user_id)
                | (CompanyMember.user_id == user_id)
            )
            .distinct()
            .order_by(Company.created_at.desc())
        )

        result = await db.execute(stmt)

        return list(result.scalars().all())