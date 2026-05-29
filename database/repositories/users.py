from database.client import AsyncDatabaseClient


class UserRepository:
    def __init__(self, client: AsyncDatabaseClient) -> None:
        self._client: AsyncDatabaseClient = client

    async def current_global_score(self, user_id: int) -> int:
        row = await self._client.fetchone(
            "SELECT global_chat_score FROM users WHERE user_id = $1",
            [user_id],
        )
        return row["global_chat_score"] if row else 0

    async def award_global_xp(self, user_id: int, delta: int) -> None:
        await self._client.execute(
            "INSERT INTO users (user_id, global_chat_score) VALUES ($1, $2) "
            "ON CONFLICT (user_id) DO UPDATE SET global_chat_score = users.global_chat_score + $2",
            [user_id, delta],
        )
