from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

path = Path(__file__).parent.parent.parent.absolute() / '.env'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=path, extra='allow')
    DOCUMENT_API_ENDPOINT: str
    DOCUMENT_DATABASE_PATH: str
    IS_DEBUG: bool = False

    @property
    def sqlalchemy_url(self):
        return f"sql+asyncydb://{self.DOCUMENT_API_ENDPOINT}{self.DOCUMENT_DATABASE_PATH}"
