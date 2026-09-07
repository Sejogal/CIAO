from uuid import UUID

from sqlalchemy import select
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