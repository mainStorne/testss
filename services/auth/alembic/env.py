import asyncio
import os
from logging.config import fileConfig

from alembic.ddl import DefaultImpl
from sqlalchemy import pool, Table, MetaData, Column, String, Integer
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from ydb import AccessTokenCredentials
from ydb.aio.iam import MetadataUrlCredentials



# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata


from application.db import Base
from application.settings import Settings

target_metadata = Base.metadata
settings = Settings()

config.set_main_option('sqlalchemy.url', settings.sqlalchemy_url)


class YDBImpl(DefaultImpl):
    __dialect__ = "yql"


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    if not settings.IS_DEBUG:
        kwargs = {
            "connect_args": {
                'credentials': AccessTokenCredentials(os.environ.get('YDB_ACCESS_TOKEN')),
                'protocol': 'grpcs'}
        }
    else:
        kwargs = {}

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        **kwargs
    )

    async with connectable.connect() as connection:
        context.configure(
            connection.sync_connection, target_metadata=target_metadata
        )
        ctx = context.get_context()
        ctx._version = Table(
            ctx.version_table,
            MetaData(),
            Column("version_num", String(32), nullable=False),
            Column("id", Integer, nullable=True, primary_key=True),
        )

        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
