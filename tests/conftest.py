from fastapi.testclient import TestClient
from services.api.src.app import app
from pytest import fixture

@fixture(scope='session')
def client():
    with TestClient(app) as client:
        yield client
