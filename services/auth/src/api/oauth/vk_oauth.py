from typing import Optional

from httpx_oauth.oauth2 import GetAccessTokenError

from .base import BaseOAuth2, OAuth2Response, GetUserInfoError
from ...conf import settings
from pydantic import BaseModel, ConfigDict


class VKUser(BaseModel):
    model_config = ConfigDict(extra='allow')
    user_id: str
    first_name: str
    last_name: str
    phone: str
    avatar: str
    email: str


class VKUserInfo(BaseModel):
    user: VKUser


class VKOAuth2(BaseOAuth2):

    def __init__(self):
        super().__init__(settings.YANDEX_CLIENT_ID, settings.YANDEX_CLIENT_SECRET,
                         "https://oauth.yandex.ru/authorize",
                         "https://id.vk.com/oauth2/auth ",
                         'https://id.vk.com/oauth2/user_info ',
                         refresh_token_endpoint="https://oauth.yandex.ru/token",
                         name='vk',
                         token_endpoint_auth_method='client_secret_post')

        self.redirect_uri = '/auth/vk/callback'

    async def get_access_token(
            self, code: str, code_verifier: str,
            device_id: str,
            state: str,
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
                "code_verifier": code_verifier,
                'device_id': device_id,
                'rredirection_uri': self.redirect_uri,
                'state': state,
            }

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

    async def get_user_info(self, token: str):
        """
        raise GetUserInfoError
        :param token:
        :return:
        """
        async with self.get_httpx_client() as client:
            response = await client.post(self.user_info_endpoint,
                                         params={"access_token": token, 'client_id': self.client_id})
        return self.parse_response_to_model(VKUserInfo, response, exc_class=GetUserInfoError)
