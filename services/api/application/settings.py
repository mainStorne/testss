from pathlib import Path

from pydantic import field_validator, _BaseMultiHostUrl
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env", case_sensitive=True, extra="allow"
    )
    # PostgreSQL Database Connection
    DOCUMENT_API_ENDPOINT: str
    DOCUMENT_DATABASE_PATH: str

    @property
    def db_connection_string(self) -> str:


        return 'yql+ydb_async'

        # return str(
        #     _BaseMultiHostUrl.build(
        #         scheme="yql+ydb",
        #         username=info.data["POSTGRES_USER"],
        #         password=info.data["POSTGRES_PASSWORD"],
        #         host=info.data["POSTGRES_HOST"],
        #         port=info.data["POSTGRES_PORT"],
        #         path=info.data["POSTGRES_DB"],
        #     )
        # )
        #
        #
