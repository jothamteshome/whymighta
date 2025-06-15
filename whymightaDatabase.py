import asyncio
import asyncmy
import datetime
import whymightaGlobalVariables
import logging

from asyncmy.cursors import DictCursor
from core.config import config
from whymightaSupportFunctions import md5_hash

logging.getLogger('asyncmy').setLevel(logging.ERROR)


async def connect_async(retries=5, delay=2):
    for attempt in range(1, retries+1):
        try:
            return await asyncmy.connect(
                host=config.MYSQL_HOST,
                user=config.MYSQL_USERNAME,
                password=config.MYSQL_PASSWORD,
                database=config.MYSQL_DATABASE,
                port=int(config.MYSQL_PORT),
                connect_timeout=10
            )
        except asyncmy.errors.OperationalError as e:
            print(f"[DB Retry] Attempt {attempt} failed: {e}")
            if attempt == retries:
                raise  # Re-raise after last attempt
            await asyncio.sleep(delay * (2 ** (attempt - 1)))


# Query the database
async def query_database(statement, parameters=None):
    conn = await connect_async()

    async with conn.cursor(DictCursor) as cur:
        if parameters is not None:
            await cur.execute(statement, parameters)
        else:
            await cur.execute(statement)

        rows = await cur.fetchall()

    await conn.commit()
    await conn.ensure_closed()

    return rows


async def create_tables(table_paths='database'):
    # Create new tables
    tables = ["guilds", 'users', 'games', 'threads']

    for table in tables:
        with open(f"{table_paths}/{table}.sql", "r") as sql_table:
            await query_database(" ".join(sql_table.readlines()))


async def insert_rows(table, columns, parameters):
    conn = await connect_async()
    
    col_string = ", ".join(columns)
    param_string = ", ".join(['%s'] * len(columns))
    insert_statement = f"INSERT IGNORE INTO {table} ({col_string}) VALUES ({param_string});"
    
    async with conn.cursor(DictCursor) as cursor:
        await cursor.executemany(insert_statement, parameters)
        await conn.commit()
        last_id = cursor.lastrowid
        
    await conn.ensure_closed()
    return last_id


# Add guild id to 'guilds' table
async def add_guild(guild_id, default_channel_id):
    await insert_rows('guilds', ['guild_id', 'bot_channel_id'], [(guild_id, default_channel_id)])


# Removes guild id from `guilds` table
async def remove_guild(guild_id):
    await query_database("DELETE FROM `guilds` WHERE `guild_id` = %s", [guild_id])


# Add encrypted user id and guild id to 'users' table
async def add_user(user_id, guild_id):
    await insert_rows('users', ['user_id', 'guild_id', 'user_chat_score'], [(user_id, guild_id, 0)])


# Adds multiple users at once
async def add_users(user_ids, guild_id):
    user_list = [(user_id, guild_id, 0) for user_id in user_ids]
    await insert_rows('users', ['user_id', 'guild_id', 'user_chat_score'], user_list)


# Remove user id and guild id from `users` table
async def remove_user(user_id, guild_id):
    await query_database("DELETE FROM `users` WHERE `user_id` = %s AND `guild_id` = %s", [user_id, guild_id])


# Check a users current chat score
async def current_user_score(user_id, guild_id):
    current_score = await query_database("SELECT `user_chat_score` FROM `users` WHERE `user_id` = %s AND `guild_id` = %s", [user_id, guild_id])

    return current_score[0]['user_chat_score']


# Update's user's server score by amount
async def update_user_score(user_id, guild_id, increased_score):
    await query_database("UPDATE `users` SET `user_chat_score` = %s WHERE `user_id` = %s AND `guild_id` = %s", [increased_score, user_id, guild_id])


# Toggles the mock status of the guild in the database
async def toggle_mock(guild_id):
    await set_toggles_off(guild_id, 'mock')

    current_status = await query_mock(guild_id)

    if current_status:
        await query_database("UPDATE `guilds` SET `mock` = %s WHERE `guild_id` = %s", [0, guild_id])
        current_status = False
    else:
        await query_database("UPDATE `guilds` SET `mock` = %s WHERE `guild_id` = %s", [1, guild_id])
        current_status = True

    return current_status


async def toggle_binary(guild_id):
    await set_toggles_off(guild_id, 'binary')

    current_status = await query_binary(guild_id)

    if current_status:
        await query_database("UPDATE `guilds` SET `binary` = %s WHERE `guild_id` = %s", [0, guild_id])
        current_status = False
    else:
        await query_database("UPDATE `guilds` SET `binary` = %s WHERE `guild_id` = %s", [1, guild_id])
        current_status = True

    return current_status


async def set_toggles_off(guild_id, called_from):
    toggle_columns = {"mock", "binary"}

    toggle_columns.remove(called_from)

    for col in toggle_columns:
        await query_database(f"UPDATE `guilds` SET `{col}` = %s WHERE `guild_id` = %s", [0, guild_id])


# Query's database for mocking status
async def query_mock(guild_id):
    current_status = await query_database("SELECT `mock` FROM `guilds` WHERE `guild_id` = %s", [guild_id])

    return current_status[0]['mock']


async def query_binary(guild_id):
    current_status = await query_database("SELECT `binary` FROM `guilds` WHERE `guild_id` = %s", [guild_id])

    return current_status[0]['binary']


async def update_last_message_sent(guild_id, updated_time):
    await query_database("UPDATE `guilds` SET `last_message_sent` = %s WHERE `guild_id` = %s", [updated_time, guild_id])


async def query_last_message_sent(guild_id):
    message_sent = await query_database("SELECT `last_message_sent` FROM `guilds` WHERE `guild_id` = %s", [guild_id])

    return message_sent[0]['last_message_sent'].replace(tzinfo=datetime.timezone.utc)


async def get_bot_text_channel_id(guild_id):
    channel_id = await query_database("SELECT `bot_channel_id` FROM `guilds` WHERE `guild_id` = %s", [guild_id])

    # If channel id doesn't exist, return None
    if not channel_id:
        return None
    
    return channel_id[0]['bot_channel_id']


async def set_bot_text_channel_id(guild_id, channel_id):
    await query_database("UPDATE `guilds` SET `bot_channel_id` = %s WHERE `guild_id` = %s;", [channel_id, guild_id])


async def get_game_from_list(guild_id, game_name):
    game = await query_database("SELECT `game_name` FROM `games` WHERE `guild_id` = %s AND `game_hash` = %s", [guild_id, md5_hash(game_name.lower())])

    return game


async def get_all_games_from_list(guild_id):
    game_list = await query_database("SELECT `game_name` FROM `games` WHERE `guild_id` = %s", [guild_id])

    return game_list


async def add_game_to_list(guild_id, game_name):
    await insert_rows('games', ['guild_id', 'game_name', 'game_hash'], [(guild_id, game_name, md5_hash(game_name.lower()))])


async def remove_game_from_list(guild_id, game_name):
    await query_database("DELETE FROM `games` WHERE `guild_id` = %s AND `game_hash` = %s", [guild_id, md5_hash(game_name.lower())])


async def set_thread_id(thread_id, guild_id, user_id):
    await insert_rows('threads', ['thread_id', 'guild_id', 'user_id'], [(thread_id, guild_id, user_id)])


async def get_thread_id(guild_id, user_id):
    thread_id = await query_database("SELECT `thread_id` FROM `threads` WHERE `guild_id` = %s AND `user_id` = %s", [guild_id, user_id])

    return thread_id[0]['thread_id'] if thread_id else None


async def remove_thread_id(thread_id):
    await query_database("DELETE FROM `threads` WHERE `thread_id` = %s", [thread_id])