import aiofiles
import datetime
import logging
from pathlib import Path
from typing import Optional

import asyncpg

from database.client import AsyncDatabaseClient
from database.repositories.guilds import GuildRepository
from database.repositories.users import UserRepository
from database.repositories.guild_members import GuildMemberRepository
from database.repositories.games import GameRepository
from database.repositories.threads import ThreadRepository

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, *, client: AsyncDatabaseClient) -> None:
        self._client: AsyncDatabaseClient = client
        self._guilds: GuildRepository = GuildRepository(client)
        self._users: UserRepository = UserRepository(client)
        self._guild_members: GuildMemberRepository = GuildMemberRepository(client)
        self._games: GameRepository = GameRepository(client)
        self._threads: ThreadRepository = ThreadRepository(client)

    async def init_pool(self) -> None:
        await self._client.init_pool()

    async def close_pool(self) -> None:
        await self._client.close_pool()

    async def migrate_v2(self) -> None:
        """One-time migration: guild-scoped users table → global users + guild_members."""
        gm_exists = await self._client.fetchone(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = 'guild_members'"
        )
        if gm_exists:
            return

        old_users_exists = await self._client.fetchone(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'guild_id'"
        )
        if not old_users_exists:
            return

        logger.info("migrate_v2: starting migration from guild-scoped users to global users + guild_members")

        async with self._client.transaction() as conn:
            await conn.execute(
                "ALTER TABLE guilds ADD COLUMN IF NOT EXISTS active BOOLEAN NOT NULL DEFAULT TRUE"
            )

            await conn.execute("""
                CREATE TABLE users_new (
                    user_id           BIGINT  PRIMARY KEY,
                    global_chat_score INT     NOT NULL DEFAULT 0
                )
            """)
            await conn.execute(
                "CREATE INDEX idx_users_new_global_score ON users_new (global_chat_score DESC)"
            )

            await conn.execute("""
                INSERT INTO users_new (user_id, global_chat_score)
                SELECT user_id, SUM(user_chat_score)
                FROM users
                GROUP BY user_id
            """)

            await conn.execute("""
                CREATE TABLE guild_members (
                    user_id             BIGINT   NOT NULL,
                    guild_id            BIGINT   NOT NULL,
                    guild_chat_score    INT      NOT NULL DEFAULT 0,
                    active              BOOLEAN  NOT NULL DEFAULT TRUE,
                    PRIMARY KEY (user_id, guild_id),
                    CONSTRAINT gm_users_fk  FOREIGN KEY (user_id)  REFERENCES users_new (user_id),
                    CONSTRAINT gm_guilds_fk FOREIGN KEY (guild_id) REFERENCES guilds (guild_id)
                )
            """)
            await conn.execute(
                "CREATE INDEX idx_guild_members_guild_id ON guild_members (guild_id)"
            )
            await conn.execute(
                "CREATE INDEX idx_guild_members_guild_score ON guild_members (guild_id, guild_chat_score DESC)"
            )

            await conn.execute("""
                INSERT INTO guild_members (user_id, guild_id, guild_chat_score, active)
                SELECT user_id, guild_id, user_chat_score, TRUE
                FROM users
            """)

            fk_name = await conn.fetchval("""
                SELECT tc.constraint_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                WHERE tc.table_schema = 'public'
                AND tc.table_name = 'threads'
                AND tc.constraint_type = 'FOREIGN KEY'
                AND kcu.column_name = 'user_id'
                LIMIT 1
            """)
            if fk_name:
                safe_name = await conn.fetchval("SELECT quote_ident($1)", fk_name)
                await conn.execute(f"ALTER TABLE threads DROP CONSTRAINT {safe_name}")
            await conn.execute("""
                ALTER TABLE threads ADD CONSTRAINT threads_gm_fk
                FOREIGN KEY (user_id, guild_id) REFERENCES guild_members (user_id, guild_id)
            """)

            await conn.execute("DROP TABLE users")
            await conn.execute("ALTER TABLE users_new RENAME TO users")
            await conn.execute(
                "ALTER INDEX idx_users_new_global_score RENAME TO idx_users_global_score"
            )

        logger.info("migrate_v2: completed successfully")

    async def create_tables(self, table_paths: str = "database/sql") -> None:
        tables = ["guilds", "users", "guild_members", "games", "threads"]
        for table in tables:
            async with aiofiles.open(Path(table_paths) / f"{table}.sql", "r") as f:
                sql = await f.read()
            await self._client.execute(sql)

    # ---- Guilds ----

    async def add_guild(self, guild_id: int, default_channel_id: Optional[int]) -> None:
        await self._guilds.add(guild_id, default_channel_id)

    async def activate_guild(self, guild_id: int) -> None:
        await self._guilds.activate_guild(guild_id)

    async def deactivate_guild(self, guild_id: int) -> None:
        await self._guilds.deactivate_guild(guild_id)

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

    async def get_theme(self, guild_id: int) -> Optional[dict]:
        return await self._guilds.get_theme(guild_id)

    async def set_theme(self, guild_id: int, theme: dict) -> None:
        await self._guilds.set_theme(guild_id, theme)

    async def clear_theme(self, guild_id: int) -> None:
        await self._guilds.clear_theme(guild_id)

    async def get_guild_config(self, guild_id: int) -> tuple[bool, bool]:
        return await self._guilds.get_guild_config(guild_id)

    # ---- Guild Members ----

    async def add_user(self, user_id: int, guild_id: int) -> None:
        await self._guild_members.add(user_id, guild_id)

    async def add_users(self, user_ids: list[int], guild_id: int) -> None:
        await self._guild_members.add_many(user_ids, guild_id)

    async def deactivate_member(self, user_id: int, guild_id: int) -> None:
        await self._guild_members.deactivate(user_id, guild_id)

    async def current_guild_score(self, user_id: int, guild_id: int) -> int:
        return await self._guild_members.current_guild_score(user_id, guild_id)

    async def award_guild_xp(
        self, user_id: int, guild_id: int, delta: int, timestamp: datetime.datetime
    ) -> None:
        await self._guild_members.award_xp(user_id, guild_id, delta, timestamp)

    async def get_leaderboard(self, guild_id: int, sort: str = "guild") -> list[asyncpg.Record]:
        return await self._guild_members.get_leaderboard(guild_id, sort)

    # ---- Users (global) ----

    async def current_global_score(self, user_id: int) -> int:
        return await self._users.current_global_score(user_id)

    async def award_global_xp(self, user_id: int, delta: int) -> None:
        await self._users.award_global_xp(user_id, delta)

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
