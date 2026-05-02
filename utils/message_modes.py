import logging

import disnake

from database.manager import Database
from utils.text_utils import convert_binary, spongebob_case

logger = logging.getLogger(__name__)


async def mock_user(db: Database, message: disnake.Message) -> None:
    if not await db.query_mock(message.guild.id):
        return
    logger.debug("Mock triggered in guild %d by user %d", message.guild.id, message.author.id)
    channel = message.channel
    if "http" in message.content.split("://")[0]:
        await channel.send(message.content)
    elif message.attachments:
        if message.content:
            await channel.send(spongebob_case(message.content))
        for attachment in message.attachments:
            await channel.send(attachment)
    else:
        await channel.send(spongebob_case(message.content))


async def binarize_message(db: Database, message: disnake.Message) -> None:
    if not await db.query_binary(message.guild.id):
        return
    logger.debug("Binary triggered in guild %d by user %d", message.guild.id, message.author.id)
    channel = message.channel
    if "http" in message.content.split("://")[0]:
        await channel.send(message.content)
    elif message.attachments:
        if message.content:
            await channel.send(convert_binary(message.content))
        for attachment in message.attachments:
            await channel.send(attachment)
    else:
        await channel.send(convert_binary(message.content))
