from .settings import Settings
from sqlmodel.ext.asyncio.session import AsyncSession
from ydb.aio.iam import MetadataUrlCredentials
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

settings = Settings()  # type: ignore
if settings.IS_DEBUG:
    engine = create_async_engine(settings.sqlalchemy_url, echo=True)
else:
    engine = create_async_engine(settings.sqlalchemy_url, connect_args={
        'credentials': MetadataUrlCredentials(),
        'protocol': 'grpcs'})

session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)



