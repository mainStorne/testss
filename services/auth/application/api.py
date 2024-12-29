from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm
from logging import getLogger

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .conf import session_maker
from .deps.session import get_session
from .schemas.tokens import PermissionToken

logger = getLogger(__name__)

r = APIRouter()


@r.post('/login', response_model=PermissionToken)
async def login(
        credentials: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_session)
):
    value = await session.execute(text('SELECT 1'))
    return PermissionToken(access_token=f'hi {value}')


@r.post('/logout')
async def logout():
    pass
