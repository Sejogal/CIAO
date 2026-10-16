from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseEntity


class AutomationRule(BaseEntity):
    __tablename__ = "automation_rules"

    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    datastream_id: Mapped[UUID] = mapped_column(ForeignKey("datastreams.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    operator: Mapped[str] = mapped_column(String(5), nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False, default="Enviar notificação")
    action_type: Mapped[str] = mapped_column(String(30), nullable=False, default="notification")
    target_datastream_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("datastreams.id", ondelete="CASCADE"), nullable=True, index=True
    )
    action_value: Mapped[object | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    cooldown_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=300)
    last_triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Notification(BaseEntity):
    __tablename__ = "notifications"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    automation_id: Mapped[UUID | None] = mapped_column(ForeignKey("automation_rules.id", ondelete="SET NULL"), nullable=True, index=True)
    datastream_id: Mapped[UUID | None] = mapped_column(ForeignKey("datastreams.id", ondelete="SET NULL"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False, default="warning")
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class DeviceCommand(BaseEntity):
    __tablename__ = "device_commands"

    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    automation_id: Mapped[UUID | None] = mapped_column(ForeignKey("automation_rules.id", ondelete="SET NULL"), nullable=True, index=True)
    datastream_id: Mapped[UUID] = mapped_column(ForeignKey("datastreams.id", ondelete="CASCADE"), nullable=False, index=True)
    value: Mapped[object] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    next_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
