import asyncpg
from contextlib import asynccontextmanager
from typing import Optional
from urllib.parse import quote_plus


class AsyncDatabaseClient:
    def __init__(
        self,
        *,
        host: str,
        user: str,
        password: str,
        db: str,
        port: int,
        minsize: int = 3,
        maxsize: int = 10,
    ) -> None:
        self._host: str = host
        self._user: str = user
        self._password: str = password
        self._db: str = db
        self._port: int = port
        self._connection_string: str = f"postgres://{user}:{quote_plus(password)}@{host}:{port}/{db}"
        self._min_size: int = minsize
        self._max_size: int = maxsize
        self._pool: Optional[asyncpg.Pool] = None

    async def init_pool(self) -> None:
        self._pool = await asyncpg.create_pool(
            self._connection_string,
            min_size=self._min_size,
            max_size=self._max_size,
        )

    async def close_pool(self) -> None:
        if self._pool:
            await self._pool.close()
            self._pool = None

    @asynccontextmanager
    async def _get_connection(self):
        async with self._pool.acquire() as conn:
            yield conn

    # ---- Basic Queries ----

    async def fetchall(self, query: str, params: list | None = None) -> list[asyncpg.Record]:
        async with self._get_connection() as conn:
            return await conn.fetch(query, *(params or ()))

    async def fetchone(self, query: str, params: list | None = None) -> asyncpg.Record | None:
        async with self._get_connection() as conn:
            return await conn.fetchrow(query, *(params or ()))

    async def execute(self, query: str, params: list | None = None) -> None:
        async with self._get_connection() as conn:
            await conn.execute(query, *(params or ()))

    async def executemany(self, query: str, params_list: list) -> None:
        async with self._get_connection() as conn:
            await conn.executemany(query, params_list)

    # ---- Transactions ----

    @asynccontextmanager
    async def transaction(self):
        async with self._get_connection() as conn:
            async with conn.transaction():
                yield conn
