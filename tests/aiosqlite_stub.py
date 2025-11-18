from __future__ import annotations

import asyncio
import sqlite3
from functools import partial
from typing import Any, Iterable, Optional

__all__ = [
    "connect",
    "Connection",
    "Cursor",
    "Error",
    "IntegrityError",
]

Error = sqlite3.Error
DatabaseError = sqlite3.DatabaseError
IntegrityError = sqlite3.IntegrityError
NotSupportedError = sqlite3.NotSupportedError
OperationalError = sqlite3.OperationalError
ProgrammingError = sqlite3.ProgrammingError
sqlite_version = sqlite3.sqlite_version
sqlite_version_info = sqlite3.sqlite_version_info


def _run_sync(fn, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return loop.run_in_executor(None, partial(fn, *args, **kwargs))


class Cursor:
    def __init__(self, cursor: sqlite3.Cursor):
        self._cursor = cursor
        self.arraysize = 1

    @property
    def description(self):
        return self._cursor.description

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    @property
    def rowcount(self):
        return self._cursor.rowcount

    async def execute(self, *args, **kwargs):
        await _run_sync(self._cursor.execute, *args, **kwargs)
        return self

    async def executemany(self, *args, **kwargs):
        await _run_sync(self._cursor.executemany, *args, **kwargs)
        return self

    async def fetchone(self):
        return await _run_sync(self._cursor.fetchone)

    async def fetchmany(self, size: Optional[int] = None):
        size = size or self.arraysize
        return await _run_sync(self._cursor.fetchmany, size)

    async def fetchall(self):
        return await _run_sync(self._cursor.fetchall)

    async def close(self):
        await _run_sync(self._cursor.close)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()


class Connection:
    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection

    async def cursor(self) -> Cursor:
        cursor = await _run_sync(self._connection.cursor)
        return Cursor(cursor)

    async def execute(self, *args, **kwargs):
        cursor = await self.cursor()
        await cursor.execute(*args, **kwargs)
        return cursor

    async def executemany(self, *args, **kwargs):
        cursor = await self.cursor()
        await cursor.executemany(*args, **kwargs)
        return cursor

    async def executescript(self, script: str):
        await _run_sync(self._connection.executescript, script)

    async def commit(self):
        await _run_sync(self._connection.commit)

    async def rollback(self):
        await _run_sync(self._connection.rollback)

    async def close(self):
        await _run_sync(self._connection.close)

    async def create_function(self, *args, **kwargs):
        await _run_sync(self._connection.create_function, *args, **kwargs)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self.close()



class _ConnectCoroutine:
    def __init__(self, database: str, kwargs: dict[str, Any]):
        self.database = database
        self.kwargs = kwargs
        self.daemon = False

    def __await__(self):
        return self._run().__await__()

    async def _run(self) -> Connection:
        connect_callable = partial(sqlite3.connect, self.database, **self.kwargs)
        connection = await _run_sync(connect_callable)
        connection.row_factory = sqlite3.Row
        return Connection(connection)


def connect(database: str, **kwargs) -> _ConnectCoroutine:
    kwargs.setdefault("check_same_thread", False)
    return _ConnectCoroutine(database, kwargs)

