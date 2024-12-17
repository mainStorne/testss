from httpx import AsyncClient, ASGITransport
from src.application.app import app
from pytest import fixture

@fixture(scope='session')
async def client():
    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        yield client
