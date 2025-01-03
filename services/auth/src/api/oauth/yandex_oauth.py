from pydantic import BaseModel, field_validator, ValidationError, ConfigDict, Field
from .base import BaseOAuth2
from logging import getLogger
from ...conf import settings

logger = getLogger(__name__)


class YandexUserInfo(BaseModel):
    model_config = ConfigDict(extra='allow')
    first_name: str
    last_name: str
    display_name: str
    real_name: str
    login: str
    default_email: str
    default_avatar_id: str
    id: int
    client_id: str
    psuid: str


class YandexOAuth2(BaseOAuth2):
    """
    Yandex OAuth2
    """

    def __init__(self):
        super().__init__(settings.YANDEX_CLIENT_ID, settings.YANDEX_CLIENT_SECRET,
                         "https://oauth.yandex.ru/authorize",
                         "https://oauth.yandex.ru/token",
                         user_info_endpoint="https://login.yandex.ru/info",
                         refresh_token_endpoint="https://oauth.yandex.ru/token",
                         name='yandex',
                         token_endpoint_auth_method='client_secret_basic')

    async def get_user_info(self, token: str) -> YandexUserInfo:
        """
                raise GetUserInfoError
                :param token:
                :return:
                """
        return await super().get_user_info(token, YandexUserInfo)
