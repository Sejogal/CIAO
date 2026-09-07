from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import decode_token
from app.db.dependencies import get_db
from app.modules.identity.model import User
from app.modules.identity.role_model import Role
from app.modules.identity.service import IdentityService


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/identity/login"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:

    # 1. Decodificar JWT
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Obter user_id do JWT
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Buscar usuário + Role + Permissions
    stmt = (
        select(User)
        .options(
            selectinload(User.role)
            .selectinload(Role.permissions)
        )
        .where(User.id == UUID(user_id))
    )

    result = await db.execute(stmt)

    user = result.scalar_one_or_none()

    # 4. Usuário não encontrado
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 5. Usuário inativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user



async def get_identity_service(
    db: AsyncSession = Depends(get_db),
) -> IdentityService:
    return IdentityService(db)


def require_permission(permission_name: str):
    async def permission_checker(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        # Usuário sem role
        if not current_user.role_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no assigned role",
            )

        # Busca a permissão através da role do usuário
        stmt = (
            select(User)
            .where(User.id == current_user.id)
        )

        result = await db.execute(stmt)
        user = result.scalar_one()

        # Carrega a role e suas permissões explicitamente
        await db.refresh(user, ["role"])

        role = user.role

        if not role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no assigned role",
            )

        # Evita lazy-loading assíncrono
        await db.refresh(role, ["permissions"])

        has_permission = any(
            permission.name == permission_name
            for permission in role.permissions
        )

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission_name}",
            )

        return current_user

    return permission_checker
