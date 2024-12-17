import schemathesis
from schemathesis import Case
from pytest import fixture
from httpx import AsyncClient
schemathesis.experimental.OPEN_API_3_1.enable()
schema = schemathesis.from_uri('http://127.0.0.1:8000/openapi.json')

class Auth:

    def get(self, case, ctx):
        return 'dima'

    def set(self, case: Case, data, ctx):
        case.headers['api_key'] = data


@schema.auth(Auth)
@schema.include(path='/', method='POST').parametrize()
def test_api(case:Case):

    print(case)
    case.call_and_validate()
