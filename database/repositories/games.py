import hashlib
from typing import Optional

import asyncpg

from database.client import AsyncDatabaseClient


def _md5_hash(value: str) -> str:
    return hashlib.md5(value.encode("utf-8")).hexdigest()


class GameRepository:
    def __init__(self, client: AsyncDatabaseClient) -> None:
        self._client: AsyncDatabaseClient = client

    async def get(self, guild_id: int, game_name: str) -> Optional[asyncpg.Record]:
        return await self._client.fetchone(
            "SELECT game_name FROM games WHERE guild_id = $1 AND game_hash = $2",
            [guild_id, _md5_hash(game_name.lower())],
        )

    async def get_all(self, guild_id: int) -> list[asyncpg.Record]:
        return await self._client.fetchall(
            "SELECT game_name FROM games WHERE guild_id = $1",
            [guild_id],
        )

    async def add(self, guild_id: int, game_name: str) -> None:
        await self._client.execute(
            "INSERT INTO games (guild_id, game_name, game_hash) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
            [guild_id, game_name, _md5_hash(game_name.lower())],
        )

    async def remove(self, guild_id: int, game_name: str) -> None:
        await self._client.execute(
            "DELETE FROM games WHERE guild_id = $1 AND game_hash = $2",
            [guild_id, _md5_hash(game_name.lower())],
        )
