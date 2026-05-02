import asyncio
import logging
import os

import disnake
from disnake.ext import commands

from core.config import config
from database.client import AsyncDatabaseClient
from database.manager import Database
from utils import message_modes, startup, xp
from utils.logging_config import configure_logger

configure_logger()
logger = logging.getLogger(__name__)

bot = commands.InteractionBot(intents=disnake.Intents.all())

_client = AsyncDatabaseClient(
    host=config.DB_HOST,
    user=config.DB_USERNAME,
    password=config.DB_PASSWORD,
    db=config.DB_DATABASE,
    port=config.DB_PORT,
)
database = Database(client=_client)
bot.db = database


@bot.event
async def on_ready() -> None:
    await startup.update_new_members(bot, database)
    await startup.server_message_catchup(bot, database)
    logger.info("Logged in as %s", bot.user)


@bot.event
async def on_message(message: disnake.Message) -> None:
    if message.author.bot is not True:
        if bot.user in message.mentions:
            cog = bot.get_cog("Chatbot")
            if cog:
                await cog.chatting(message)
        await xp.give_message_xp(database, bot, message, catching_up=False)
        await message_modes.mock_user(database, message)
        await message_modes.binarize_message(database, message)


@bot.event
async def on_guild_join(guild: disnake.Guild) -> None:
    member_ids = [member.id for member in guild.members if not member.bot]
    default_channel_id = guild.text_channels[0].id if guild.text_channels else None
    await database.add_guild(guild.id, default_channel_id)
    await database.add_users(member_ids, guild.id)


@bot.event
async def on_guild_remove(guild: disnake.Guild) -> None:
    await database.remove_guild(guild.id)


@bot.event
async def on_application_command(inter: disnake.ApplicationCommandInteraction) -> None:
    await bot.process_application_commands(inter)
    await xp.give_inter_xp(database, bot, inter, catching_up=False)


@bot.event
async def on_member_join(member: disnake.Member) -> None:
    await database.add_user(member.id, member.guild.id)


@bot.event
async def on_member_remove(member: disnake.Member) -> None:
    await database.remove_user(member.id, member.guild.id)


@bot.event
async def on_guild_channel_delete(channel: disnake.abc.GuildChannel) -> None:
    bot_text_channel_id = await database.get_bot_text_channel_id(channel.guild.id)
    if channel.id == bot_text_channel_id:
        default_channel_id = channel.guild.text_channels[0].id if channel.guild.text_channels else None
        await database.set_bot_text_channel_id(channel.guild.id, default_channel_id)


# Load cogs from the 'cogs' directory
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        name, ext = os.path.splitext(filename)
        bot.load_extension(f"cogs.{name}")


async def main() -> None:
    await database.init_pool()
    await database.create_tables()
    try:
        await bot.start(config.DISCORD_TOKEN)
    finally:
        await database.close_pool()


if __name__ == "__main__":
    asyncio.run(main())