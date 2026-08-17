from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.core.config import settings
from app.modules.identity.credential_model import Credential
from app.modules.identity.model import User
from app.modules.identity.refresh_token_model import RefreshToken
from app.modules.identity.schemas import RegisterRequest


class IdentityService:

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

        user = User(
            full_name=data.full_name,
            email=data.email,
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

    @staticmethod
    async def login(
        db: AsyncSession,
        email: str,
        password: str,
    ):

        user = await IdentityService.get_user_by_email(
            db,
            email,
        )

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

        credential = await IdentityService.get_credential_for_user(
            db,
            user.id,
        )

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

        db.add(stored_refresh_token)

        await db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    async def refresh_access_token(
        db: AsyncSession,
        refresh_token: str,
    ):

        try:
            payload = decode_refresh_token(
                refresh_token
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        stmt = select(RefreshToken).where(
            RefreshToken.token == refresh_token,
            RefreshToken.revoked == False,
        )

        result = await db.execute(stmt)

        stored_token = result.scalar_one_or_none()

        if not stored_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token revoked or not found",
            )

        if stored_token.expires_at <= datetime.now(timezone.utc):

            stored_token.revoked = True

            await db.commit()

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired",
            )

        # Rotação do refresh token
        stored_token.revoked = True

        new_access_token = create_access_token(
            user_id
        )

        new_refresh_token = create_refresh_token(
            user_id
        )

        new_stored_refresh_token = RefreshToken(
            user_id=stored_token.user_id,
            token=new_refresh_token,
            expires_at=(
                datetime.now(timezone.utc)
                + timedelta(
                    days=settings.REFRESH_TOKEN_EXPIRE_DAYS
                )
            ),
        )

        db.add(new_stored_refresh_token)

        await db.commit()

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
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

        return {
            "message": "Até breve!"
        }