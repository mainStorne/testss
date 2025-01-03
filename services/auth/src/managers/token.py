from .base import BaseManager
from ..conf import settings
from ..db import UserToken, User
from datetime import datetime, timezone, timedelta
from sqlalchemy import delete, select
from uuid import UUID
import jwt
from sqlmodel.ext.asyncio.session import AsyncSession
from ..responses import MissingTokenOrInactiveUserException, UnauthorizedInvalidDataException


class TokenManager(BaseManager):
    def __init__(
            self,
            key: str,
            refresh_token_lifetime: timedelta,
            access_token_lifetime: timedelta,
            algorithm: str = "HS256",

    ):
        super().__init__(UserToken)
        self.algorithm = algorithm
        self.key = key
        self.access_token_lifetime = access_token_lifetime
        self.refresh_token_lifetime = refresh_token_lifetime

    async def refresh_token(self, session: AsyncSession, refresh_token: str):
        payload = self.decode_token(refresh_token)
        stmt = select(User, UserToken).join(UserToken).where(User.id == payload['sub']).where(
            UserToken.refresh_token == refresh_token)
        res = (await session.exec(stmt)).one()

        await session.delete(res.UserToken)

        access_token, refresh_token = self.generate_pair_of_tokens(res.User.id)
        user_token = UserToken(user_id=res.User.id, access_token=access_token, refresh_token=refresh_token)
        session.add(user_token)
        await session.commit()
        return access_token, refresh_token

    def generate_pair_of_tokens(self, user_id: UUID):
        payload = {"sub": str(user_id)}
        payload['exp'] = datetime.now(timezone.utc) + self.access_token_lifetime
        access_token = jwt.encode(payload, self.key, algorithm=self.algorithm)
        payload['exp'] = datetime.now(timezone.utc) + self.refresh_token_lifetime
        refresh_token = jwt.encode(payload, self.key, algorithm=self.algorithm)
        return access_token, refresh_token

    async def authenticate(
            self, access_token: str, session: AsyncSession
    ):
        res = self.decode_token(access_token)

        stmt = select(User).join(UserToken).where(UserToken.access_token == access_token).where(
            UserToken.user_id == res['sub'])
        return (await session.exec(stmt)).scalar()

    def decode_token(self, token: str):
        """
        :raises MissingTokenOrInactiveUserException
        :param token:
        :return:
        """
        try:
            payload = jwt.decode(
                token, self.key, algorithms=[self.algorithm]
            )
            payload['sub'] = UUID(payload['sub'])

        except (jwt.PyJWTError, ValueError, jwt.ExpiredSignatureError):
            raise MissingTokenOrInactiveUserException
        return payload

    async def logout(self, session: AsyncSession, user_id: UUID, access_token: str) -> None:
        res = self.decode_token(access_token)
        if res['sub'] != user_id:
            raise UnauthorizedInvalidDataException

        stmt = delete(UserToken).where(UserToken.access_token == access_token).where(UserToken.user_id == user_id)
        res = await session.exec(stmt)
        await session.commit()

    async def login(self, session: AsyncSession, user_id: UUID) -> UserToken:
        access_token, refresh_token = self.generate_pair_of_tokens(user_id)
        user_token = UserToken(user_id=user_id, access_token=access_token, refresh_token=refresh_token)
        session.add(user_token)
        await session.commit()
        return user_token


token_manager = TokenManager(settings.JWT_PRIVATE_KEY, access_token_lifetime=timedelta(days=2),
                             refresh_token_lifetime=timedelta(days=30))
