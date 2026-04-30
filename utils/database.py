import datetime
import hashlib

from utils.db_client import AsyncDatabaseClient


class Database:
    def __init__(self, *, client: AsyncDatabaseClient):
        self._client = client

    async def init_pool(self):
        await self._client.init_pool()

    async def close_pool(self):
        await self._client.close_pool()


    async def create_tables(self, table_paths='database'):
        tables = ['guilds', 'users', 'games', 'threads']
        for table in tables:
            with open(f"{table_paths}/{table}.sql", "r") as f:
                await self._client.execute(f.read())

    # ---- Guilds ----

    async def add_guild(self, guild_id, default_channel_id):
        await self._client.execute(
            "INSERT INTO guilds (guild_id, bot_channel_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
            [guild_id, default_channel_id]
        )

    async def remove_guild(self, guild_id):
        await self._client.execute(
            "DELETE FROM guilds WHERE guild_id = $1",
            [guild_id]
        )

    async def toggle_mock(self, guild_id):
        await self._client.execute(
            "UPDATE guilds SET binary_mode = FALSE WHERE guild_id = $1",
            [guild_id]
        )
        row = await self._client.fetchone(
            "UPDATE guilds SET mock_mode = NOT mock_mode WHERE guild_id = $1 RETURNING mock_mode",
            [guild_id]
        )
        return row['mock_mode']

    async def toggle_binary(self, guild_id):
        await self._client.execute(
            "UPDATE guilds SET mock_mode = FALSE WHERE guild_id = $1",
            [guild_id]
        )
        row = await self._client.fetchone(
            "UPDATE guilds SET binary_mode = NOT binary_mode WHERE guild_id = $1 RETURNING binary_mode",
            [guild_id]
        )
        return row['binary_mode']

    async def query_mock(self, guild_id):
        row = await self._client.fetchone(
            "SELECT mock_mode FROM guilds WHERE guild_id = $1",
            [guild_id]
        )
        return row['mock_mode']

    async def query_binary(self, guild_id):
        row = await self._client.fetchone(
            "SELECT binary_mode FROM guilds WHERE guild_id = $1",
            [guild_id]
        )
        return row['binary_mode']

    async def update_last_message_sent(self, guild_id, updated_time):
        await self._client.execute(
            "UPDATE guilds SET last_message_sent = $1 WHERE guild_id = $2",
            [updated_time, guild_id]
        )

    async def query_last_message_sent(self, guild_id):
        row = await self._client.fetchone(
            "SELECT last_message_sent FROM guilds WHERE guild_id = $1",
            [guild_id]
        )
        return row['last_message_sent']

    async def get_bot_text_channel_id(self, guild_id):
        row = await self._client.fetchone(
            "SELECT bot_channel_id FROM guilds WHERE guild_id = $1",
            [guild_id]
        )
        if not row:
            return None
        return row['bot_channel_id']

    async def set_bot_text_channel_id(self, guild_id, channel_id):
        await self._client.execute(
            "UPDATE guilds SET bot_channel_id = $1 WHERE guild_id = $2",
            [channel_id, guild_id]
        )

    # ---- Users ----

    async def add_user(self, user_id, guild_id):
        await self._client.execute(
            "INSERT INTO users (user_id, guild_id, user_chat_score) VALUES ($1, $2, 0) ON CONFLICT DO NOTHING",
            [user_id, guild_id]
        )

    async def add_users(self, user_ids, guild_id):
        await self._client.executemany(
            "INSERT INTO users (user_id, guild_id, user_chat_score) VALUES ($1, $2, 0) ON CONFLICT DO NOTHING",
            [(user_id, guild_id) for user_id in user_ids]
        )

    async def remove_user(self, user_id, guild_id):
        await self._client.execute(
            "DELETE FROM users WHERE user_id = $1 AND guild_id = $2",
            [user_id, guild_id]
        )

    async def current_user_score(self, user_id, guild_id):
        row = await self._client.fetchone(
            "SELECT user_chat_score FROM users WHERE user_id = $1 AND guild_id = $2",
            [user_id, guild_id]
        )
        return row['user_chat_score']

    async def update_user_score(self, user_id, guild_id, increased_score):
        await self._client.execute(
            "UPDATE users SET user_chat_score = $1 WHERE user_id = $2 AND guild_id = $3",
            [increased_score, user_id, guild_id]
        )

    # ---- Games ----

    def _md5_hash(self, value):
        return hashlib.md5(value.encode('utf-8')).hexdigest()

    async def get_game_from_list(self, guild_id, game_name):
        return await self._client.fetchone(
            "SELECT game_name FROM games WHERE guild_id = $1 AND game_hash = $2",
            [guild_id, self._md5_hash(game_name.lower())]
        )

    async def get_all_games_from_list(self, guild_id):
        return await self._client.fetchall(
            "SELECT game_name FROM games WHERE guild_id = $1",
            [guild_id]
        )

    async def add_game_to_list(self, guild_id, game_name):
        await self._client.execute(
            "INSERT INTO games (guild_id, game_name, game_hash) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
            [guild_id, game_name, self._md5_hash(game_name.lower())]
        )

    async def remove_game_from_list(self, guild_id, game_name):
        await self._client.execute(
            "DELETE FROM games WHERE guild_id = $1 AND game_hash = $2",
            [guild_id, self._md5_hash(game_name.lower())]
        )

    # ---- Threads ----

    async def set_thread_id(self, thread_id, guild_id, user_id):
        await self._client.execute(
            "INSERT INTO threads (thread_id, guild_id, user_id) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
            [thread_id, guild_id, user_id]
        )

    async def get_thread_id(self, guild_id, user_id):
        row = await self._client.fetchone(
            "SELECT thread_id FROM threads WHERE guild_id = $1 AND user_id = $2",
            [guild_id, user_id]
        )
        return row['thread_id'] if row else None

    async def remove_thread_id(self, thread_id):
        await self._client.execute(
            "DELETE FROM threads WHERE thread_id = $1",
            [thread_id]
        )