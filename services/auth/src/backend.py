from typing import Annotated, Optional
from .responses import UnauthorizedException, UnauthorizedInvalidDataException, ForbidException
from .db import User
from .schemas import PermissionToken
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.base import SecurityBase
from fastapi.security.http import get_authorization_scheme_param
from sqlalchemy.ext.asyncio import AsyncSession
from .deps.session import get_session
from .managers import token_manager


class Security(HTTPBearer):
    async def __call__(
            self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        authorization = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            raise UnauthorizedException
        if scheme.lower() != "bearer":
            raise UnauthorizedInvalidDataException
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)


class AuthBackend:

    def __init__(self, security: SecurityBase):
        self.security = security

    def authenticate(self, active: bool = True, verified: bool = False, superuser: bool = False):
        security = self.security

        async def wrapped(
                cred: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                session: AsyncSession = Depends(get_session)
        ):
            user = await token_manager.authenticate(cred.credentials, session)
            exc = UnauthorizedException
            if user:
                exc = ForbidException
                if active and not user.is_active:
                    exc = UnauthorizedException
                    user = None
                elif (
                        verified and not user.is_verified or superuser and not user.is_superuser
                ):
                    user = None

            if not user:
                raise exc

            return user

        return wrapped

    async def login(self, session: AsyncSession, user: User) -> PermissionToken:
        token = await token_manager.login(session, user.id)
        return PermissionToken(access_token=token.access_token, refresh_token=token.refresh_token)

    async def logout(self, session: AsyncSession, user: User, cred: HTTPAuthorizationCredentials):
        return await token_manager.logout(session, user.id, cred.credentials)

    async def refresh_token(self, session: AsyncSession, refresh_token: str):
        access_token, refresh_token = await token_manager.refresh_token(session, refresh_token)
        return PermissionToken(access_token=access_token, refresh_token=refresh_token)


auth_backend = AuthBackend(security=Security())
