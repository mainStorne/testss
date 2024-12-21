from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm
from logging import getLogger

from .schemas.tokens import PermissionToken

logger = getLogger(__name__)

r = APIRouter()


@r.post('/login', response_model=PermissionToken)
async def login(
        credentials: OAuth2PasswordRequestForm = Depends(),
):
    return PermissionToken(access_token='hi')


@r.post('/logout')
async def logout():
    pass
