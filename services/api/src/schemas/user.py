from pydantic import BaseModel


class BaseUser(BaseModel):
    name: str


class ReadUser(BaseUser):
    id: int