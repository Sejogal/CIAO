from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db
from app.modules.companies.schema import (
    CompanyCreate,
    CompanyMemberCreate,
    CompanyMemberResponse,
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
    current_user: User = Depends(
        require_permission("companies:read")
    ),
    db: AsyncSession = Depends(get_db),
):
    return await CompanyService.list_mine(
        db,
        current_user.id,
    )


@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
)
async def get_company(
    company_id: UUID,
    current_user: User = Depends(
        require_permission("companies:read")
    ),
    db: AsyncSession = Depends(get_db),
):
    return await CompanyService.get(
        db,
        company_id,
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