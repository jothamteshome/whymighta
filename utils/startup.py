import logging
from datetime import datetime, timezone

import disnake
from disnake.ext import commands

from database.manager import Database
from utils import xp

logger = logging.getLogger(__name__)


async def update_new_members(bot: commands.InteractionBot, db: Database) -> None:
    for guild in bot.guilds:
        member_ids = [member.id for member in guild.members if not member.bot]
        default_channel_id = guild.text_channels[0].id if guild.text_channels else None
        await db.add_guild(guild.id, default_channel_id)
        await db.add_users(member_ids, guild.id)
        logger.info("Synced guild %d (%s): %d members", guild.id, guild.name, len(member_ids))


async def server_message_catchup(bot: commands.InteractionBot, db: Database) -> None:
    for guild in bot.guilds:
        last_seen = await db.query_last_message_sent(guild.id)
        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
        last_server_message_time = (
            last_seen if (last_seen is not None and last_seen > epoch) else guild.created_at
        )
        logger.info(
            "Catching up guild %d (%s) from %s",
            guild.id,
            guild.name,
            last_server_message_time.isoformat(),
        )

        latest_message_time = last_server_message_time
        total_messages = 0

        for channel in guild.channels:
            if not isinstance(channel, disnake.TextChannel):
                continue

            try:
                new_messages = await channel.history(
                    after=last_server_message_time, oldest_first=True
                ).flatten()
            except (disnake.Forbidden, disnake.HTTPException) as e:
                logger.debug("Skipping channel %d in guild %d: %s", channel.id, guild.id, e)
                continue

            for message in new_messages:
                if message.interaction_metadata is None and not message.author.bot:
                    await xp.give_message_xp(db, bot, message, catching_up=True)
                    total_messages += 1

            if new_messages and new_messages[-1].created_at > latest_message_time:
                latest_message_time = new_messages[-1].created_at

        await db.update_last_message_sent(guild.id, latest_message_time)
        logger.info(
            "Catchup complete for guild %d (%s): %d messages processed",
            guild.id,
            guild.name,
            total_messages,
        )
