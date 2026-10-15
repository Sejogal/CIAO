from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db

from app.modules.identity.dependencies import (
    get_current_user,
    get_identity_service,
)
from app.modules.identity.model import User

from uuid import UUID

from app.modules.identity.schemas import (
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    UserRoleUpdate,
)

from app.modules.identity.service import IdentityService
from app.modules.identity.dependencies import require_permission
from fastapi.security import OAuth2PasswordRequestForm
from app.modules.identity.role_model import Role
from app.modules.identity.dependencies import require_permission


router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        return await IdentityService.register(
            db,
            data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


#Login
@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    service = IdentityService(db)

    return await service.login(
        email=form_data.username,
        password=form_data.password,
    )

#ME
@router.get(
    "/me",
    response_model=UserResponse,
)
async def me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(User)
        .options(
            selectinload(User.role)
            .selectinload(Role.permissions)
        )
        .where(User.id == current_user.id)
    )

    result = await db.execute(stmt)

    user = result.scalar_one()

    permissions = [
        permission.name
        for permission in user.role.permissions
    ] if user.role else []

    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "avatar": user.avatar,
        "language": user.language,
        "timezone": user.timezone,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "role": user.role,
        "permissions": permissions,
    }


#refresh
@router.post(
    "/refresh",
    response_model=TokenResponse,
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    service = IdentityService(db)

    try:
        return await service.refresh_access_token(
            request.refresh_token
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )

@router.post("/logout")
async def logout(
    request: LogoutRequest,
    db: AsyncSession = Depends(get_db),
):
    service = IdentityService(db)

    await service.logout(
        request.refresh_token
    )

    return {
        "message": "Logout realizado com sucesso"
    }

@router.patch(
    "/users/{user_id}/role",
    response_model=UserResponse,
)
async def update_user_role(
    user_id: UUID,
    data: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(
        require_permission("users:update")
    ),
):
    user = await IdentityService.update_user_role(
        db,
        user_id=user_id,
        role_name=data.role_name,
    )

    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "avatar": user.avatar,
        "language": user.language,
        "timezone": user.timezone,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "role": user.role,
        "permissions": [
            permission.name
            for permission in user.role.permissions
        ] if user.role else [],
    }


@router.post("/seed-rbac")
async def seed_rbac_endpoint(
    db: AsyncSession = Depends(get_db),
):
    from app.modules.identity.seed import seed_rbac

    await seed_rbac(db)

    return {
        "message": "RBAC inicializado com sucesso"
    }

@router.get(
    "/test-project-read",
)
async def test_project_read(
    current_user: User = Depends(
        require_permission("projects:read")
    ),
):
    return {
        "message": "Tens permissão para visualizar projetos",
        "user": current_user.email,
    }

@router.get(
    "/test-project-delete",
)
async def test_project_delete(
    current_user: User = Depends(
        require_permission("projects:delete")
    ),
):
    return {
        "message": "Tens permissão para eliminar projetos",
        "user": current_user.email,
    }


@router.get(
    "/test-permission",
    dependencies=[
        Depends(require_permission("devices:delete"))
    ],
)
async def test_permission():
    return {
        "message": "Permission granted"
    }