from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.security.api_key import APIKeyHeader
from fastapi.security.oauth2 import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from logging import getLogger

from .schemas.tokens import PermissionToken

logger = getLogger(__name__)

r = APIRouter()

@r.post('/login', response_model=PermissionToken)
async def login(
        username: Annotated[str, Body()],
        password: Annotated[str, Body()],
):
    return PermissionToken(access_token='hi')

@r.post('/logout')
async def logout():
    pass