from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity
from app.modules.identity.role_permission_model import RolePermission

if TYPE_CHECKING:
    from app.modules.identity.permission_model import Permission
    from app.modules.identity.model import User


class Role(BaseEntity):
    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary=RolePermission.__table__,
        back_populates="roles",
        lazy="selectin",

    )

    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="role",
    )