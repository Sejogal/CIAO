from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity

from uuid import UUID


if TYPE_CHECKING:
    from app.modules.identity.credential_model import Credential
    from app.modules.identity.role_model import Role
    from app.modules.projects.model import Project


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
    role_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("roles.id"),
        nullable=True,
        index=True,
    )

    role: Mapped["Role | None"] = relationship(
        "Role",
        back_populates="users",
        lazy="selectin",

    )

    projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan",
    )