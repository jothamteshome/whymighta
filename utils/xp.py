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
    mentions_xp = len(message.mentions) * 5
    attachments_xp = len(message.attachments) * 10
    content_xp = len(message.content)

    prev_xp = await db.current_user_score(message.author.id, message.guild.id)
    curr_xp = prev_xp + mentions_xp + attachments_xp + content_xp

    logger.debug(
        "Message XP: user=%d guild=%d +%d -> %d (catching_up=%s)",
        message.author.id,
        message.guild.id,
        curr_xp - prev_xp,
        curr_xp,
        catching_up,
    )

    if not catching_up:
        await announce_level_up(db, bot, prev_xp, curr_xp, message.author, message.channel)

    await db.update_user_score(message.author.id, message.guild.id, curr_xp)
    await db.update_last_message_sent(message.guild.id, message.created_at)


async def give_inter_xp(
    db: Database,
    bot: commands.InteractionBot,
    inter: disnake.ApplicationCommandInteraction,
    catching_up: bool,
) -> None:
    if inter.data.name == "level":
        return
    score = 5 + sum(len(opt) for opt in inter.options)

    prev_xp = await db.current_user_score(inter.author.id, inter.guild_id)
    curr_xp = prev_xp + score

    logger.debug(
        "Interaction XP: user=%d guild=%d command=%s +%d -> %d",
        inter.author.id,
        inter.guild_id,
        inter.data.name,
        score,
        curr_xp,
    )

    if not catching_up:
        await announce_level_up(db, bot, prev_xp, curr_xp, inter.author, inter.channel)

    await db.update_user_score(inter.author.id, inter.guild_id, curr_xp)
    await db.update_last_message_sent(inter.guild.id, inter.created_at)
