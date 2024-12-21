from fastapi import APIRouter, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.security.oauth2 import OAuth2PasswordBearer
from starlette import status

from .schemas.user import ReadUser, BaseUser
from logging import getLogger

logger = getLogger(__name__)

r = APIRouter()


val = 'dima'
api_key = APIKeyHeader(name='api_key')
oauth2 = OAuth2PasswordBearer(tokenUrl='https://d5dsupapvtpbigih7i1l.apigw.yandexcloud.net/api/auth/login')

@r.get('/')
async def index(key=Depends(oauth2)):
    if key != val:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid API key')
    return {'hello': 'world'}




@r.post('/', responses={404: {'description': 'Not found'}, status.HTTP_403_FORBIDDEN: {'description': 'Invalid API key'}})
async def index(user: BaseUser, key = Depends(api_key)):
    logger.info(key)
    if key != val:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Invalid API key')
    return ReadUser(id=1, **user.model_dump())
