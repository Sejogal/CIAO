from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity


class Project(BaseEntity):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    company_id: Mapped[UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    owner = relationship(
        "User",
        foreign_keys=[owner_id],
    )

    company = relationship(
        "Company",
        foreign_keys=[company_id],
    )
    devices = relationship(
        "Device",
        back_populates="project",
        cascade="all, delete-orphan",
    )