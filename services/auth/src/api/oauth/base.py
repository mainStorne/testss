import time
from secrets import token_urlsafe
from typing import Optional, Literal, List, Type, Dict, Any, TypeVar
from urllib.parse import urlencode

import httpx
from httpx_oauth.oauth2 import OAuth2RequestError, GetAccessTokenError, BaseOAuth2 as _BaseOAuth2, \
    OAuth2ClientAuthMethod
from pydantic import BaseModel, field_validator, ValidationError, ConfigDict, Field
from logging import getLogger

logger = getLogger(__name__)

Model = TypeVar('Model', bound=BaseModel)


class OAuth2Response(BaseModel):
    token_type: str
    access_token: str
    expires_in: int
    refresh_token: str
    scope: str | None = None

    @field_validator('expires_in', mode='after')
    def validate_expires_in(cls, expires_in: int) -> int:
        return int(time.time()) + int(expires_in)

    def is_expired(self) -> bool:
        return time.time() > self.expires_in


class GetUserInfoError(OAuth2RequestError):
    pass


class BaseOAuth2(_BaseOAuth2):

    def __init__(
            self,
            client_id: str,
            client_secret: str,
            authorize_endpoint: str,
            access_token_endpoint: str,
            user_info_endpoint:str,
            refresh_token_endpoint: Optional[str] = None,
            revoke_token_endpoint: Optional[str] = None,
            *,
            name: str = "oauth2",
            base_scopes: Optional[List[str]] = None,
            token_endpoint_auth_method: OAuth2ClientAuthMethod = "client_secret_post",
            revocation_endpoint_auth_method: Optional[OAuth2ClientAuthMethod] = None,
    ):
        super().__init__(client_id, client_secret, authorize_endpoint, access_token_endpoint, refresh_token_endpoint,
                         revoke_token_endpoint, name=name, base_scopes=base_scopes,
                         token_endpoint_auth_method=token_endpoint_auth_method,
                         revocation_endpoint_auth_method=revocation_endpoint_auth_method)

        self.user_info_endpoint = user_info_endpoint
        self.request_headers = {
            "Accept": "application/json",
            'Content-type': 'application/x-www-form-urlencoded'
        }

    async def get_access_token(
            self, code: str, code_verifier: Optional[str] = None,
            *args, **kwargs
    ) -> OAuth2Response:
        """
        Requests an access token using the authorization code obtained
        after the user has authorized the application.

        Args:
            code: The authorization code.
            redirect_uri: The URL where the user was redirected after authorization.
            code_verifier: Optional code verifier used
                in the [PKCE](https://datatracker.ietf.org/doc/html/rfc7636)) flow.

        Raises:
            GetAccessTokenError: An error occurred while getting the access token.

        Examples:
            ```py
            access_token = await client.get_access_token("CODE", "https://www.tintagel.bt/oauth-callback")
            ```
        """
        async with self.get_httpx_client() as client:
            data = {
                "grant_type": "authorization_code",
                "code": code,
            }

            if code_verifier:
                data["code_verifier"] = code_verifier

            request, auth = self.build_request(
                client,
                "POST",
                self.access_token_endpoint,
                auth_method=self.token_endpoint_auth_method,
                data=data,
            )
            response = await self.send_request(
                client, request, auth, exc_class=GetAccessTokenError
            )

            return self.parse_response_to_model(OAuth2Response, response, exc_class=GetAccessTokenError)

    def parse_response_to_model[Model](
            self, model: type[Model], response: httpx.Response, *, exc_class: Type[OAuth2RequestError]
    ) -> Model:
        try:
            return model.model_validate_json(response.content)
        except ValidationError as e:
            message = "Invalid JSON content"
            raise exc_class(message, response) from e

    async def refresh_token(self, refresh_token: str):
        """
        Requests a new access token using a refresh token.

        Args:
            refresh_token: The refresh token.

        Returns:
            An access token response dictionary.

        Raises:
            RefreshTokenError: An error occurred while refreshing the token.
            RefreshTokenNotSupportedError: The provider does not support token refresh.

        Examples:
            ```py
            access_token = await client.refresh_token("REFRESH_TOKEN")
            ```
        """
        async with self.get_httpx_client() as client:
            request, auth = self.build_request(
                client,
                "POST",
                self.refresh_token_endpoint,
                auth_method=self.token_endpoint_auth_method,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
            )
            # response = await self.send_request(
            #     client, request, auth, exc_class=RefreshTokenError
            # )
            # TODO
            # return self.(response, exc_class=RefreshTokenError)

    @property
    def authorization_url(self):
        """

        :return:
        """
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            'force_confirm': 1
        }

        return f"{self.authorize_endpoint}?{urlencode(params)}"

    async def get_user_info[model](self, token: str, modelT: type[model]) -> model:
        """
        raise GetUserInfoError
        :param token:
        :return:
        """
        async with self.get_httpx_client() as client:
            response = await client.get(self.user_info_endpoint, headers={
                'Authorization': f'OAuth {token}'})
        return self.parse_response_to_model(modelT, response, exc_class=GetUserInfoError)
