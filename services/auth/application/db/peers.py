from sqlalchemy.orm import Mapped
from .base import Base, UUIDMixin


class Peer(UUIDMixin, Base):
    __tablename__ = 'peers'
