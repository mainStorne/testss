from uuid import UUID

from sqlmodel import Field, Relationship
from sqlalchemy import PrimaryKeyConstraint
from ..schemas.users import UserRead
from ..schemas import PermissionToken


class User(UserRead, table=True):
    __tablename__ = 'users'
    password: str
    user_tokens: list['UserToken'] = Relationship(back_populates='user')


class UserToken(PermissionToken, table=True):
    __tablename__ = 'user_tokens'
    user_id: UUID = Field(foreign_key='users.id')
    user: User = Relationship(back_populates='user_tokens')
    __table_args__ = (PrimaryKeyConstraint('user_id', 'access_token', 'refresh_token'),)
