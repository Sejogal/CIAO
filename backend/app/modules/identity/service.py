from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.modules.identity.credential_model import Credential
from app.modules.identity.model import User
from app.modules.identity.refresh_token_model import RefreshToken
from app.modules.identity.role_model import Role
from app.modules.identity.schemas import RegisterRequest
from app.core.security import decode_refresh_token
from app.core.config import settings

DEFAULT_SELF_SIGNUP_ROLE = "user"


class IdentityService:

    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    async def register(
        db: AsyncSession,
        data: RegisterRequest,
    ) -> User:

        stmt = select(User).where(User.email == data.email)

        result = await db.execute(stmt)

        user = result.scalar_one_or_none()

        if user:
            raise ValueError(
                "Já existe um utilizador com este e-mail."
            )

        default_role_result = await db.execute(
            select(Role).where(Role.name == DEFAULT_SELF_SIGNUP_ROLE)
        )
        default_role = default_role_result.scalar_one_or_none()

        user = User(
            full_name=data.full_name,
            email=data.email,
            role_id=default_role.id if default_role else None,
        )

        db.add(user)

        await db.flush()

        credential = Credential(
            user_id=user.id,
            provider="password",
            password_hash=hash_password(data.password),
        )

        db.add(credential)

        await db.commit()

        await db.refresh(user)

        return user

    @staticmethod
    async def update_user_role(
        db: AsyncSession,
        user_id: UUID,
        role_name: str,
    ) -> User:

        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        role_result = await db.execute(
            select(Role).where(Role.name == role_name)
        )
        role = role_result.scalar_one_or_none()

        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role '{role_name}' does not exist",
            )

        user.role_id = role.id

        await db.commit()

        refreshed_result = await db.execute(
            select(User)
            .options(
                selectinload(User.role).selectinload(Role.permissions)
            )
            .where(User.id == user_id)
            .execution_options(populate_existing=True)
        )

        return refreshed_result.scalar_one()

    @staticmethod
    async def get_user_by_email(
        db: AsyncSession,
        email: str,
    ) -> User | None:

        stmt = select(User).where(
            User.email == email
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    async def get_credential_for_user(
        db: AsyncSession,
        user_id,
    ) -> Credential | None:

        stmt = select(Credential).where(
            Credential.user_id == user_id,
            Credential.provider == "password",
        )

        result = await db.execute(stmt)

        return result.scalar_one_or_none()


    #LOGIN
    async def login(
        self,
        email: str,
        password: str,
    ):
        stmt = select(User).where(
            User.email == email
        )

        result = await self.db.execute(stmt)

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        stmt = select(Credential).where(
            Credential.user_id == user.id,
            Credential.provider == "password",
        )

        result = await self.db.execute(stmt)

        credential = result.scalar_one_or_none()

        if not credential:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not verify_password(
            password,
            credential.password_hash,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        access_token = create_access_token(
            str(user.id)
        )

        refresh_token = create_refresh_token(
            str(user.id)
        )

        stored_refresh_token = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=(
                datetime.now(timezone.utc)
                + timedelta(
                    days=settings.REFRESH_TOKEN_EXPIRE_DAYS
                )
            ),
        )

        self.db.add(stored_refresh_token)

        await self.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    

    #Refresh-acess-token
    async def refresh_access_token(
        self,
        refresh_token: str,
    ):
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise ValueError(
                "Invalid or expired refresh token"
            )

        if payload.get("type") != "refresh":
            raise ValueError(
                "Invalid token type"
            )

        user_id = payload.get("sub")

        if not user_id:
            raise ValueError(
                "Invalid refresh token"
            )

        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token == refresh_token,
                RefreshToken.revoked == False,
            )
        )

        stored_token = result.scalar_one_or_none()

        if not stored_token:
            raise ValueError(
                "Refresh token revoked or not found"
            )

        if stored_token.expires_at <= datetime.now(timezone.utc):
            raise ValueError(
                "Refresh token expired"
            )

        access_token = create_access_token(
            user_id
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }



    @staticmethod
    async def logout(
        db: AsyncSession,
        refresh_token: str,
    ):

        stmt = select(RefreshToken).where(
            RefreshToken.token == refresh_token
        )

        result = await db.execute(stmt)

        stored_token = result.scalar_one_or_none()

        if stored_token:
            stored_token.revoked = True

            await db.commit()

    def __init__(self, db: AsyncSession):
        self.db = db