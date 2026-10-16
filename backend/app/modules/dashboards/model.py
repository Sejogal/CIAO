from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity


class Dashboard(BaseEntity):
    __tablename__ = "dashboards"

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    layout: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    widgets = relationship(
        "Widget", back_populates="dashboard", cascade="all, delete-orphan"
    )


class Widget(BaseEntity):
    __tablename__ = "widgets"

    dashboard_id: Mapped[UUID] = mapped_column(
        ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=False, index=True
    )
    datastream_id: Mapped[UUID] = mapped_column(
        ForeignKey("datastreams.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    widget_type: Mapped[str] = mapped_column(String(40), nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    position: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    dashboard = relationship("Dashboard", back_populates="widgets")
