from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.modules.companies.schemas import (
    CompanyCreate,
    CompanyMemberCreate,
    CompanyMemberDetailedResponse,
    CompanyMemberResponse,
    CompanyMemberUpdate,
    CompanyResponse,
    CompanyUpdate,
)

from app.modules.companies.service import CompanyService

from app.modules.identity.dependencies import (
    get_current_user,
    require_permission,
)

from app.modules.identity.model import User


router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


# ============================================================
# COMPANIES
# ============================================================

@router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_company(
    data: CompanyCreate,
    current_user: User = Depends(
        require_permission("companies:create")
    ),
    db: AsyncSession = Depends(get_db),
):
    return await CompanyService.create(
        db,
        current_user.id,
        data,
    )


@router.get(
    "",
    response_model=list[CompanyResponse],
)
async def list_companies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_permission("companies:read")
    ),
):
    return await CompanyService.list_for_user(
        db,
        current_user.id,
    )


# ============================================================
# COMPANY MEMBERS
# ============================================================

@router.post(
    "/{company_id}/members",
    response_model=CompanyMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_member(
    company_id: UUID,
    data: CompanyMemberCreate,
    current_user: User = Depends(
        require_permission("companies:manage_members")
    ),
    db: AsyncSession = Depends(get_db),
):
    return await CompanyService.add_member(
        db,
        company_id,
        current_user.id,
        data,
    )


@router.get(
    "/{company_id}/members",
    response_model=list[CompanyMemberDetailedResponse],
)
async def list_members(
    company_id: UUID,
    current_user: User = Depends(
        require_permission("companies:read")
    ),
    db: AsyncSession = Depends(get_db),
):
    return await CompanyService.list_members(
        db,
        company_id,
        current_user.id,
    )


@router.patch(
    "/{company_id}/members/{user_id}",
    response_model=CompanyMemberResponse,
)
async def update_member(
    company_id: UUID,
    user_id: UUID,
    data: CompanyMemberUpdate,
    current_user: User = Depends(
        require_permission("companies:manage_members")
    ),
    db: AsyncSession = Depends(get_db),
):
    return await CompanyService.update_member(
        db,
        company_id,
        current_user.id,
        user_id,
        data,
    )


@router.delete(
    "/{company_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_member(
    company_id: UUID,
    user_id: UUID,
    current_user: User = Depends(
        require_permission("companies:manage_members")
    ),
    db: AsyncSession = Depends(get_db),
):
    await CompanyService.remove_member(
        db,
        company_id,
        current_user.id,
        user_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )


# ============================================================
# COMPANY DETAILS
# ============================================================

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_permission("companies:read")
    ),
):
    return await CompanyService.get_for_user(
        db,
        company_id,
        current_user.id,
    )


@router.patch(
    "/{company_id}",
    response_model=CompanyResponse,
)
async def update_company(
    company_id: UUID,
    data: CompanyUpdate,
    current_user: User = Depends(
        require_permission("companies:update")
    ),
    db: AsyncSession = Depends(get_db),
):
    return await CompanyService.update(
        db,
        company_id,
        current_user.id,
        data,
    )