from sqlalchemy.orm import DeclarativeBase

from app.db.mixins import (
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)


class Base(DeclarativeBase):
    pass


class BaseEntity(
    UUIDMixin,
    TimestampMixin,
    SoftDeleteMixin,
    Base,
):
    """
    Classe base para todas as entidades.
    """

    __abstract__ = True


