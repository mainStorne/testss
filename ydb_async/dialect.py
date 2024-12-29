from typing import Type

from sqlalchemy import URL, Pool, AsyncAdaptedQueuePool
from ydb_sqlalchemy.sqlalchemy import AsyncYqlDialect, AdaptedAsyncConnection
from ydb_sqlalchemy.sqlalchemy.dbapi_adapter import AdaptedAsyncCursor
from sqlalchemy.util import await_only
from ydb_dbapi.utils import CursorStatus


class AsyncCursor(AdaptedAsyncCursor):
    def fetchone(self):
        return self._cursor._fetchone_from_buffer()

    def fetchmany(self, size=None):
        size = size or self.arraysize
        return self._cursor._fetchmany_from_buffer(size)

    def fetchall(self):
        return self._cursor._fetchall_from_buffer()

    def close(self):
        self._cursor._state = CursorStatus.closed


class AsyncConnection(AdaptedAsyncConnection):
    def cursor(self):
        return AsyncCursor(self._connection.cursor())


class Dialect(AsyncYqlDialect):
    driver = 'asyncydb'

    def __init__(self, json_serializer=None,
                 json_deserializer=None,
                 **kwargs):
        super().__init__(json_serializer=json_serializer, json_deserializer=json_deserializer,
                         _add_declare_for_yql_stmt_vars=True, **kwargs)

    def connect(self, *cargs, **cparams):
        return AsyncConnection(await_only(self.dbapi.async_connect(*cargs, **cparams)))

    def get_dialect_pool_class(self, url: URL) -> Type[Pool]:
        return AsyncAdaptedQueuePool
