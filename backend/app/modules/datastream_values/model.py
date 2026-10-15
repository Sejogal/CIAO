from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseEntity


class DatastreamValue(BaseEntity):
    __tablename__ = "datastream_values"
    __table_args__ = (
        Index(
            "ix_datastream_values_datastream_id_recorded_at",
            "datastream_id",
            "recorded_at",
        ),
    )

    datastream_id: Mapped[UUID] = mapped_column(
        ForeignKey("datastreams.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Stored as JSONB so a single table can hold whatever type the parent
    # Datastream declares (boolean/integer/float/string/json) without one
    # column per type; the service layer validates it against
    # Datastream.data_type before it ever reaches here.
    value: Mapped[Any] = mapped_column(
        JSONB,
        nullable=False,
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    datastream = relationship(
        "Datastream",
        back_populates="values",
    )
