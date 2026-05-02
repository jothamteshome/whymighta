from typing import Optional

from database.client import AsyncDatabaseClient


class ThreadRepository:
    def __init__(self, client: AsyncDatabaseClient) -> None:
        self._client: AsyncDatabaseClient = client

    async def set(self, thread_id: int, guild_id: int, user_id: int) -> None:
        await self._client.execute(
            "INSERT INTO threads (thread_id, guild_id, user_id) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
            [thread_id, guild_id, user_id],
        )

    async def get(self, guild_id: int, user_id: int) -> Optional[int]:
        row = await self._client.fetchone(
            "SELECT thread_id FROM threads WHERE guild_id = $1 AND user_id = $2",
            [guild_id, user_id],
        )
        return row["thread_id"] if row else None

    async def remove(self, thread_id: int) -> None:
        await self._client.execute(
            "DELETE FROM threads WHERE thread_id = $1",
            [thread_id],
        )
