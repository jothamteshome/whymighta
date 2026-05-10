import datetime
from typing import Optional

from database.client import AsyncDatabaseClient


class GuildRepository:
    def __init__(self, client: AsyncDatabaseClient) -> None:
        self._client: AsyncDatabaseClient = client

    async def add(self, guild_id: int, default_channel_id: Optional[int]) -> None:
        await self._client.execute(
            "INSERT INTO guilds (guild_id, bot_channel_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            [guild_id, default_channel_id],
        )

    async def remove(self, guild_id: int) -> None:
        await self._client.execute(
            "DELETE FROM guilds WHERE guild_id = $1",
            [guild_id],
        )

    async def toggle_mock(self, guild_id: int) -> bool:
        await self._client.execute(
            "UPDATE guilds SET binary_mode = FALSE WHERE guild_id = $1",
            [guild_id],
        )
        row = await self._client.fetchone(
            "UPDATE guilds SET mock_mode = NOT mock_mode WHERE guild_id = $1 RETURNING mock_mode",
            [guild_id],
        )
        return row["mock_mode"] if row else False

    async def toggle_binary(self, guild_id: int) -> bool:
        await self._client.execute(
            "UPDATE guilds SET mock_mode = FALSE WHERE guild_id = $1",
            [guild_id],
        )
        row = await self._client.fetchone(
            "UPDATE guilds SET binary_mode = NOT binary_mode WHERE guild_id = $1 RETURNING binary_mode",
            [guild_id],
        )
        return row["binary_mode"] if row else False

    async def get_mock(self, guild_id: int) -> bool:
        row = await self._client.fetchone(
            "SELECT mock_mode FROM guilds WHERE guild_id = $1",
            [guild_id],
        )
        return row["mock_mode"] if row else False

    async def get_binary(self, guild_id: int) -> bool:
        row = await self._client.fetchone(
            "SELECT binary_mode FROM guilds WHERE guild_id = $1",
            [guild_id],
        )
        return row["binary_mode"] if row else False

    async def update_last_message_sent(self, guild_id: int, updated_time: datetime.datetime) -> None:
        await self._client.execute(
            "UPDATE guilds SET last_message_sent = $1 WHERE guild_id = $2",
            [updated_time, guild_id],
        )

    async def get_last_message_sent(self, guild_id: int) -> Optional[datetime.datetime]:
        row = await self._client.fetchone(
            "SELECT last_message_sent FROM guilds WHERE guild_id = $1",
            [guild_id],
        )
        return row["last_message_sent"] if row else None

    async def get_bot_channel_id(self, guild_id: int) -> Optional[int]:
        row = await self._client.fetchone(
            "SELECT bot_channel_id FROM guilds WHERE guild_id = $1",
            [guild_id],
        )
        return row["bot_channel_id"] if row else None

    async def set_bot_channel_id(self, guild_id: int, channel_id: Optional[int]) -> None:
        await self._client.execute(
            "UPDATE guilds SET bot_channel_id = $1 WHERE guild_id = $2",
            [channel_id, guild_id],
        )

    async def get_theme(self, guild_id: int) -> Optional[dict]:
        row = await self._client.fetchone(
            "SELECT theme FROM guilds WHERE guild_id = $1",
            [guild_id],
        )
        return row["theme"] if row else None

    async def set_theme(self, guild_id: int, theme: dict) -> None:
        await self._client.execute(
            "UPDATE guilds SET theme = $1 WHERE guild_id = $2",
            [theme, guild_id],
        )

    async def clear_theme(self, guild_id: int) -> None:
        await self._client.execute(
            "UPDATE guilds SET theme = NULL WHERE guild_id = $1",
            [guild_id],
        )

    async def get_guild_config(self, guild_id: int) -> tuple[bool, bool]:
        row = await self._client.fetchone(
            "SELECT mock_mode, binary_mode FROM guilds WHERE guild_id = $1",
            [guild_id],
        )
        return (row["mock_mode"], row["binary_mode"]) if row else (False, False)
