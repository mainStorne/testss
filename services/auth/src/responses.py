from typing import Union

from fastapi import HTTPException, status
from pydantic import BaseModel


class ErrorModel(BaseModel):
    detail: Union[str, dict[str, str]]


def build_response(excs: list[HTTPException]):
    exc = excs[0]
    return {
        exc.status_code: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        exc.detail: {
                            "summary": exc.detail,
                            "value": {"detail": exc.detail},
                        }
                        for exc in excs
                    }
                }
            },
        }
    }


InvalidDataException = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid data')

invalid_data_response = build_response([InvalidDataException])

UnauthorizedException = HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
UnauthorizedInvalidDataException = HTTPException(status.HTTP_401_UNAUTHORIZED,
                                                 detail='Invalid authentication credentials')

MissingTokenOrInactiveUserException = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                                    detail="Missing token or inactive user.")
unauthorized_response = build_response(
    [UnauthorizedInvalidDataException, UnauthorizedException, MissingTokenOrInactiveUserException]
)

ForbidException = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
forbidden_response = build_response([ForbidException])

IncorrectCredentialsException = HTTPException(status_code=400, detail="Incorrect username or password")
incorrect_credentials_response = build_response([IncorrectCredentialsException])

auth_responses = {**unauthorized_response, **forbidden_response}
