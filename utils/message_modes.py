import disnake

from database.manager import Database
from utils.text_utils import convert_binary, spongebob_case


async def mock_user(db: Database, message: disnake.Message) -> None:
    if not await db.query_mock(message.guild.id):
        return
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
