import pytest
import schemathesis
from schemathesis import Case
from project.src.application.app import app
from pytest import fixture
from httpx import AsyncClient
schemathesis.experimental.OPEN_API_3_1.enable()
schema = schemathesis.from_asgi('/openapi.json', app)

class Auth:

    def get(self, case, ctx):
        return 'Bearer petya'

    def set(self, case: Case, data, ctx):
        case.headers = case.headers or {}
        case.headers['Authorization'] = data

@schema.auth(Auth)
@schema.parametrize()
def test_api(case:Case):
    case.call_and_validate()


@schema.parametrize()
def test_fail_api(case:Case):
    with pytest.raises(Exception):
        case.call_and_validate()
