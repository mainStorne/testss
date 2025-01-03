from .base import BaseManager
from sqlmodel import select
from fastapi.security import OAuth2PasswordRequestForm
from ..db import User
from ..exceptions import UserNotFoundException
from ..schemas import UserCreate
from .files import file_manager
from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from passlib.hash import pbkdf2_sha256


class UserManager(BaseManager):
    def __init__(self):
        super().__init__(User)

    async def login(self, session: AsyncSession, cred: OAuth2PasswordRequestForm):
        stmt = select(User).where(User.username == cred.username)
        user = (await session.exec(stmt)).first()
        if not user:
            # Run the hasher to mitigate timing attack
            # Inspired from Django: https://code.djangoproject.com/ticket/20760
            pbkdf2_sha256.hash(cred.password)
            raise UserNotFoundException
        if not pbkdf2_sha256.verify(cred.password, user.password):
            raise UserNotFoundException
        return user

    async def _create_user_with_photo(self, session: AsyncSession, user: UserCreate, exc: Exception):
        # user.photo save photo to s3 bucket
        bucket = 'user-profiles-b1grtbln15t0ipdvvmqi'
        folder = f'profiles/{user.username}'
        key = await file_manager.save_file(user.photo, bucket, folder)
        attrs = {'photo_url': file_manager._get_s3_url(bucket, key)}
        try:
            # idea with add to this method new param exc: Exception that need to raise if invalid something
            return await self.create(session, user, **attrs, exc=exc)
        except Exception as e:
            await file_manager.delete_file(bucket, key)
            raise

    async def create_user(self, session: AsyncSession, user: UserCreate, exc: Exception):

        hashed = pbkdf2_sha256.hash(user.password)
        user.password = hashed

        if user.photo:
            return await self._create_user_with_photo(session, user, exc)
        return await self.create(session, user, exc=exc)


user_manager = UserManager()
