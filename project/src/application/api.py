from fastapi import APIRouter, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from starlette import status

from .schemas.user import ReadUser, BaseUser
from logging import getLogger

logger = getLogger(__name__)

r = APIRouter()


@r.get('/')
async def index():
    return {'hello': 'world'}


val = 'dima'
api_key = APIKeyHeader(name='api_key')


@r.post('/', responses={404: {'description': 'Not found'}, status.HTTP_403_FORBIDDEN: {'description': 'Invalid API key'}})
async def index(user: BaseUser, key = Depends(api_key)):
    if key != val:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid API key')
    return ReadUser(id=1, **user.model_dump())
