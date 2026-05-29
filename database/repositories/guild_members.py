import datetime

import asyncpg

from database.client import AsyncDatabaseClient


class GuildMemberRepository:
    def __init__(self, client: AsyncDatabaseClient) -> None:
        self._client: AsyncDatabaseClient = client

    async def add(self, user_id: int, guild_id: int) -> None:
        async with self._client.transaction() as conn:
            await conn.execute(
                "INSERT INTO users (user_id) VALUES ($1) ON CONFLICT DO NOTHING",
                user_id,
            )
            await conn.execute(
                "INSERT INTO guild_members (user_id, guild_id) VALUES ($1, $2) "
                "ON CONFLICT (user_id, guild_id) DO UPDATE SET active = TRUE",
                user_id, guild_id,
            )

    async def add_many(self, user_ids: list[int], guild_id: int) -> None:
        async with self._client.transaction() as conn:
            await conn.executemany(
                "INSERT INTO users (user_id) VALUES ($1) ON CONFLICT DO NOTHING",
                [(user_id,) for user_id in user_ids],
            )
            await conn.executemany(
                "INSERT INTO guild_members (user_id, guild_id) VALUES ($1, $2) "
                "ON CONFLICT (user_id, guild_id) DO UPDATE SET active = TRUE",
                [(user_id, guild_id) for user_id in user_ids],
            )

    async def deactivate(self, user_id: int, guild_id: int) -> None:
        await self._client.execute(
            "UPDATE guild_members SET active = FALSE WHERE user_id = $1 AND guild_id = $2",
            [user_id, guild_id],
        )

    async def current_guild_score(self, user_id: int, guild_id: int) -> int:
        row = await self._client.fetchone(
            "SELECT guild_chat_score FROM guild_members WHERE user_id = $1 AND guild_id = $2",
            [user_id, guild_id],
        )
        return row["guild_chat_score"] if row else 0

    async def award_xp(
        self, user_id: int, guild_id: int, delta: int, timestamp: datetime.datetime
    ) -> None:
        """Atomically increment both guild and global scores and update the guild timestamp."""
        async with self._client.transaction() as conn:
            await conn.execute(
                "UPDATE guild_members SET guild_chat_score = guild_chat_score + $1 "
                "WHERE user_id = $2 AND guild_id = $3",
                delta, user_id, guild_id,
            )
            await conn.execute(
                "UPDATE users SET global_chat_score = global_chat_score + $1 WHERE user_id = $2",
                delta, user_id,
            )
            await conn.execute(
                "UPDATE guilds SET last_message_sent = $1 WHERE guild_id = $2",
                timestamp, guild_id,
            )

    async def get_leaderboard(self, guild_id: int, sort: str = "guild") -> list[asyncpg.Record]:
        order_col = "u.global_chat_score" if sort == "global" else "gm.guild_chat_score"
        return await self._client.fetchall(
            f"SELECT gm.user_id, gm.guild_chat_score, u.global_chat_score "
            f"FROM guild_members gm "
            f"JOIN users u ON gm.user_id = u.user_id "
            f"WHERE gm.guild_id = $1 "
            f"ORDER BY {order_col} DESC",
            [guild_id],
        )
