from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Body, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from logging import getLogger
from sqlalchemy.ext.asyncio import AsyncSession
from ..deps.session import get_session
from ..backend import auth_backend
from ..managers import user_manager
from ..schemas.tokens import PermissionToken
from ..schemas.users import UserCreate, UserRead, User
from ..exceptions import UserNotFoundException
from ..responses import invalid_data_response, InvalidDataException, unauthorized_response, \
    incorrect_credentials_response, IncorrectCredentialsException, auth_responses

logger = getLogger(__name__)

r = APIRouter()


@r.post('/register', response_model=UserRead,
        responses={**invalid_data_response})
async def user(user: UserCreate = Depends(UserCreate.as_form()),
               session: AsyncSession = Depends(get_session)):
    return await user_manager.create_user(session, user, exc=InvalidDataException)


@r.post('/login', response_model=PermissionToken, responses={**incorrect_credentials_response, **auth_responses})
async def login(
        credentials: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_session)
):
    try:
        user = await user_manager.login(session, credentials)
    except UserNotFoundException:
        raise IncorrectCredentialsException
    return await auth_backend.login(session, user)


@r.post('/logout', status_code=status.HTTP_204_NO_CONTENT,
        responses={**auth_responses})
async def logout(
        *,
        user: User = Depends(auth_backend.authenticate()),
        cred: Annotated[HTTPAuthorizationCredentials, Depends(auth_backend.security)],
        session: AsyncSession = Depends(get_session)
):
    await auth_backend.logout(session, user, cred)
    return


@r.post(
    "/refresh_token",
    response_model=PermissionToken
)
async def refresh(refresh_token: str = Body(embed=True),
                  session: AsyncSession = Depends(get_session)
                  ):
    return await auth_backend.refresh_token(session, refresh_token)
