import asyncpg
from contextlib import asynccontextmanager
from urllib.parse import quote_plus


class AsyncDatabaseClient:
    def __init__(self, *, host: str, user: str, password: str, db: str, port: int, minsize: int = 3, maxsize: int = 10):
        self._host = host
        self._user = user
        self._password = password
        self._db = db
        self._port = port

        self._connection_string = f"postgres://{user}:{quote_plus(password)}@{host}:{port}/{db}"
        self._min_size = minsize
        self._max_size = maxsize
        self._pool = None

    async def init_pool(self):
        """Initialize the asyncpg connection pool"""
        self._pool = await asyncpg.create_pool(
            self._connection_string,
            min_size=self._min_size,
            max_size=self._max_size
        )

    async def close_pool(self):
        """Close the asyncpg connection pool if it exists"""
        if self._pool:
            await self._pool.close()
            self._pool = None

    @asynccontextmanager
    async def _get_connection(self):
        """Acquire a connection from the pool"""
        async with self._pool.acquire() as conn:
            try:
                yield conn
            finally:
                pass

    # ---- Basic Queries ----

    async def fetchall(self, query, params=None):
        async with self._get_connection() as conn:
            return await conn.fetch(query, *(params or ()))

    async def fetchone(self, query, params=None):
        async with self._get_connection() as conn:
            return await conn.fetchrow(query, *(params or ()))

    async def execute(self, query: str, params=None):
        """Single insert/update/delete"""
        async with self._get_connection() as conn:
            await conn.execute(query, *(params or ()))

    async def executemany(self, query, params_list):
        """Batch insert/update/delete"""
        async with self._get_connection() as conn:
            await conn.executemany(query, params_list)

    # ---- Transactions ----

    @asynccontextmanager
    async def transaction(self):
        """Run multiple queries in a transaction"""
        async with self._get_connection() as conn:
            async with conn.transaction():
                yield conn
