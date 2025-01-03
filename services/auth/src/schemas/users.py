from sqlmodel import SQLModel, Field
from fastapi import UploadFile
from sqlalchemy import String, Column
from .mixins import UUIDMixin
from fastapi_libkit import FormBodyMixin


class User(SQLModel):
    username: str = Field(sa_column=Column(String(255), unique=True))
    email: str = Field(sa_column=Column(String(255), unique=True))


class UserCreate(FormBodyMixin, User):
    password: str
    photo: UploadFile | None = None


class UserRead(UUIDMixin, User):
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False
    photo_url: str | None = None
