from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.dialects import registry
from pathlib import Path

path = Path(__file__).parent.parent.absolute() / '.env'
registry.register('sql.asyncydb', 'ydb_async.dialect', 'Dialect')


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=path, extra='allow')
    DOCUMENT_API_ENDPOINT: str
    DOCUMENT_DATABASE_PATH: str
    IS_DEBUG: bool = False
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    JWT_PRIVATE_KEY: str

    @property
    def sqlalchemy_url(self):
        return f"sql+asyncydb://{self.DOCUMENT_API_ENDPOINT}{self.DOCUMENT_DATABASE_PATH}"
