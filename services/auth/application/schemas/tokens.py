from pydantic import BaseModel


class PermissionToken(BaseModel):
    access_token: str
