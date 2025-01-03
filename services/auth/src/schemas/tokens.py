from sqlmodel import SQLModel


class PermissionToken(SQLModel):
    access_token: str
    refresh_token: str
