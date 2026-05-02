import disnake
from disnake.ext import commands


async def clear_guild_commands(bot: commands.InteractionBot) -> list[disnake.Guild]:
    guilds = []
    for guild in bot.guilds:
        await bot.bulk_overwrite_guild_commands(guild.id, [])
        guilds.append(guild)
    return guilds
