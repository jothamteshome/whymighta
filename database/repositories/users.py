from typing import Optional

from database.client import AsyncDatabaseClient


class UserRepository:
    def __init__(self, client: AsyncDatabaseClient) -> None:
        self._client: AsyncDatabaseClient = client

    async def add(self, user_id: int, guild_id: int) -> None:
        await self._client.execute(
            "INSERT INTO users (user_id, guild_id, user_chat_score) VALUES ($1, $2, 0) ON CONFLICT DO NOTHING",
            [user_id, guild_id],
        )

    async def add_many(self, user_ids: list[int], guild_id: int) -> None:
        await self._client.executemany(
            "INSERT INTO users (user_id, guild_id, user_chat_score) VALUES ($1, $2, 0) ON CONFLICT DO NOTHING",
            [(user_id, guild_id) for user_id in user_ids],
        )

    async def remove(self, user_id: int, guild_id: int) -> None:
        await self._client.execute(
            "DELETE FROM users WHERE user_id = $1 AND guild_id = $2",
            [user_id, guild_id],
        )

    async def get_score(self, user_id: int, guild_id: int) -> int:
        row = await self._client.fetchone(
            "SELECT user_chat_score FROM users WHERE user_id = $1 AND guild_id = $2",
            [user_id, guild_id],
        )
        return row["user_chat_score"] if row else 0

    async def update_score(self, user_id: int, guild_id: int, score: int) -> None:
        await self._client.execute(
            "UPDATE users SET user_chat_score = $1 WHERE user_id = $2 AND guild_id = $3",
            [score, user_id, guild_id],
        )
