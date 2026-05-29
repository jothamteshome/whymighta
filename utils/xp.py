import logging
import math

import disnake
from disnake.ext import commands

from database.manager import Database

logger = logging.getLogger(__name__)


def check_level(score: int) -> float:
    return score ** (1 / 5)


async def announce_level_up(
    db: Database,
    bot: commands.InteractionBot,
    previous_xp: int,
    current_xp: int,
    user: disnake.Member,
    channel: disnake.TextChannel,
) -> None:
    prev_level = check_level(previous_xp)
    curr_level = check_level(current_xp)

    if math.floor(curr_level) <= math.floor(prev_level):
        return

    bot_channel_id = await db.get_bot_text_channel_id(channel.guild.id)
    target_channel = bot.get_channel(bot_channel_id) if bot_channel_id else channel
    logger.info(
        "Level up: %s reached level %d in guild %d",
        user.name,
        math.floor(curr_level),
        channel.guild.id,
    )
    await target_channel.send(
        f"Congratulations {user.mention}! You've reached Level {math.floor(curr_level)}!"
    )


async def give_message_xp(
    db: Database,
    bot: commands.InteractionBot,
    message: disnake.Message,
    catching_up: bool,
) -> None:
    delta = len(message.mentions) * 5 + len(message.attachments) * 10 + len(message.content)

    if message.guild is not None:
        prev_xp = await db.current_guild_score(message.author.id, message.guild.id)

        logger.debug(
            "Message XP: user=%d guild=%d +%d -> %d (catching_up=%s)",
            message.author.id,
            message.guild.id,
            delta,
            prev_xp + delta,
            catching_up,
        )

        if not catching_up:
            await announce_level_up(db, bot, prev_xp, prev_xp + delta, message.author, message.channel)

        await db.award_guild_xp(message.author.id, message.guild.id, delta, message.created_at)
    else:
        logger.debug("DM XP: user=%d +%d", message.author.id, delta)
        await db.award_global_xp(message.author.id, delta)


async def give_inter_xp(
    db: Database,
    bot: commands.InteractionBot,
    inter: disnake.ApplicationCommandInteraction,
    catching_up: bool,
) -> None:
    if inter.data.name in ("level", "leaderboard", "help"):
        return
    delta = 5 + sum(len(str(v)) for v in inter.options.values())

    if inter.guild_id is not None:
        prev_xp = await db.current_guild_score(inter.author.id, inter.guild_id)

        logger.debug(
            "Interaction XP: user=%d guild=%d command=%s +%d -> %d",
            inter.author.id,
            inter.guild_id,
            inter.data.name,
            delta,
            prev_xp + delta,
        )

        if not catching_up:
            await announce_level_up(db, bot, prev_xp, prev_xp + delta, inter.author, inter.channel)

        await db.award_guild_xp(inter.author.id, inter.guild_id, delta, inter.created_at)
    else:
        await db.award_global_xp(inter.author.id, delta)
