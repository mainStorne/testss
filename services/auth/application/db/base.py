from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Uuid
from uuid import uuid4


class Base(DeclarativeBase):
    pass


class UUIDMixin:
    """
    Mixin for models that have a UUID primary key.
    """
    uuid: Mapped[uuid4] = mapped_column(Uuid, primary_key=True)