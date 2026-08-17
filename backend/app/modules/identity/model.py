from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity

if TYPE_CHECKING:
    from app.modules.identity.credential_model import Credential


class User(BaseEntity):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    avatar: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    language: Mapped[str] = mapped_column(
        String(10),
        default="pt",
        nullable=False,
    )

    timezone: Mapped[str] = mapped_column(
        String(50),
        default="Africa/Luanda",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    credentials: Mapped[list["Credential"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )