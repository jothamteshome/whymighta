import aiofiles
import datetime
from pathlib import Path
from typing import Optional

import asyncpg

from database.client import AsyncDatabaseClient
from database.repositories.guilds import GuildRepository
from database.repositories.users import UserRepository
from database.repositories.games import GameRepository
from database.repositories.threads import ThreadRepository


class Database:
    def __init__(self, *, client: AsyncDatabaseClient) -> None:
        self._client: AsyncDatabaseClient = client
        self._guilds: GuildRepository = GuildRepository(client)
        self._users: UserRepository = UserRepository(client)
        self._games: GameRepository = GameRepository(client)
        self._threads: ThreadRepository = ThreadRepository(client)

    async def init_pool(self) -> None:
        await self._client.init_pool()

    async def close_pool(self) -> None:
        await self._client.close_pool()

    async def create_tables(self, table_paths: str = "database/sql") -> None:
        tables = ["guilds", "users", "games", "threads"]
        for table in tables:
            async with aiofiles.open(Path(table_paths) / f"{table}.sql", "r") as f:
                sql = await f.read()
            await self._client.execute(sql)

    # ---- Guilds ----

    async def add_guild(self, guild_id: int, default_channel_id: Optional[int]) -> None:
        await self._guilds.add(guild_id, default_channel_id)

    async def remove_guild(self, guild_id: int) -> None:
        await self._guilds.remove(guild_id)

    async def toggle_mock(self, guild_id: int) -> bool:
        return await self._guilds.toggle_mock(guild_id)

    async def toggle_binary(self, guild_id: int) -> bool:
        return await self._guilds.toggle_binary(guild_id)

    async def query_mock(self, guild_id: int) -> bool:
        return await self._guilds.get_mock(guild_id)

    async def query_binary(self, guild_id: int) -> bool:
        return await self._guilds.get_binary(guild_id)

    async def update_last_message_sent(self, guild_id: int, updated_time: datetime.datetime) -> None:
        await self._guilds.update_last_message_sent(guild_id, updated_time)

    async def query_last_message_sent(self, guild_id: int) -> Optional[datetime.datetime]:
        return await self._guilds.get_last_message_sent(guild_id)

    async def get_bot_text_channel_id(self, guild_id: int) -> Optional[int]:
        return await self._guilds.get_bot_channel_id(guild_id)

    async def set_bot_text_channel_id(self, guild_id: int, channel_id: Optional[int]) -> None:
        await self._guilds.set_bot_channel_id(guild_id, channel_id)

    # ---- Users ----

    async def add_user(self, user_id: int, guild_id: int) -> None:
        await self._users.add(user_id, guild_id)

    async def add_users(self, user_ids: list[int], guild_id: int) -> None:
        await self._users.add_many(user_ids, guild_id)

    async def remove_user(self, user_id: int, guild_id: int) -> None:
        await self._users.remove(user_id, guild_id)

    async def current_user_score(self, user_id: int, guild_id: int) -> int:
        return await self._users.get_score(user_id, guild_id)

    async def update_user_score(self, user_id: int, guild_id: int, score: int) -> None:
        await self._users.update_score(user_id, guild_id, score)

    # ---- Games ----

    async def get_game_from_list(self, guild_id: int, game_name: str) -> Optional[asyncpg.Record]:
        return await self._games.get(guild_id, game_name)

    async def get_all_games_from_list(self, guild_id: int) -> list[asyncpg.Record]:
        return await self._games.get_all(guild_id)

    async def add_game_to_list(self, guild_id: int, game_name: str) -> None:
        await self._games.add(guild_id, game_name)

    async def remove_game_from_list(self, guild_id: int, game_name: str) -> None:
        await self._games.remove(guild_id, game_name)

    # ---- Threads ----

    async def set_thread_id(self, thread_id: int, guild_id: int, user_id: int) -> None:
        await self._threads.set(thread_id, guild_id, user_id)

    async def get_thread_id(self, guild_id: int, user_id: int) -> Optional[int]:
        return await self._threads.get(guild_id, user_id)

    async def remove_thread_id(self, thread_id: int) -> None:
        await self._threads.remove(thread_id)
