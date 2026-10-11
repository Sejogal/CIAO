from __future__ import annotations

from uuid import UUID

from sqlalchemy import Boolean, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity


class Datastream(BaseEntity):
    __tablename__ = "datastreams"

    device_id: Mapped[UUID] = mapped_column(
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    data_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    unit: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    min_value: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    max_value: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    device = relationship(
        "Device",
        back_populates="datastreams",
    )