import disnake
from disnake.ext import commands

from database.manager import Database
from utils import xp


async def update_new_members(bot: commands.InteractionBot, db: Database) -> None:
    for guild in bot.guilds:
        member_ids = [member.id for member in guild.members if not member.bot]
        default_channel_id = guild.text_channels[0].id if guild.text_channels else None
        await db.add_guild(guild.id, default_channel_id)
        await db.add_users(member_ids, guild.id)


async def server_message_catchup(bot: commands.InteractionBot, db: Database) -> None:
    for guild in bot.guilds:
        last_seen = await db.query_last_message_sent(guild.id)
        last_server_message_time = last_seen or guild.created_at

        latest_message_time = last_server_message_time

        for channel in guild.channels:
            if not isinstance(channel, disnake.TextChannel):
                continue

            new_messages = await channel.history(
                after=last_server_message_time, oldest_first=True
            ).flatten()

            for message in new_messages:
                if message.interaction_metadata is None and not message.author.bot:
                    await xp.give_message_xp(db, bot, message, catching_up=True)

            if new_messages and new_messages[-1].created_at > latest_message_time:
                latest_message_time = new_messages[-1].created_at

        await db.update_last_message_sent(guild.id, latest_message_time)
