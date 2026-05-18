import logging

import disnake
from disnake.ext import commands

from database.manager import Database
from utils.theme_utils import add_theme_fields, get_guild_theme

logger = logging.getLogger(__name__)


class Info(commands.Cog):
    def __init__(self, bot: commands.InteractionBot) -> None:
        self.bot: commands.InteractionBot = bot
        self.database: Database = bot.db

    @commands.slash_command(
        description="Show bot status and configuration for this server",
        default_member_permissions=disnake.Permissions(administrator=True),
    )
    async def info(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()

        bot_channel_id = await self.database.get_bot_text_channel_id(inter.guild.id)
        if bot_channel_id:
            channel = inter.guild.get_channel(bot_channel_id)
            channel_value = channel.mention if channel else f"Unknown ({bot_channel_id})"
        else:
            channel_value = "Not set"

        mock, binary = await self.database.get_guild_config(inter.guild.id)

        theme = await get_guild_theme(self.database, inter.guild.id)

        embed = disnake.Embed(title="Bot Status", color=0x9534eb)

        embed.add_field(name="Bot Channel", value=channel_value, inline=False)
        embed.add_field(name="Mock Mode", value="On" if mock else "Off", inline=True)
        embed.add_field(name="Binary Mode", value="On" if binary else "Off", inline=True)

        if theme:
            bot_nick = inter.guild.me.nick or "None assigned"
            add_theme_fields(embed, theme, bot_nick)
        else:
            embed.add_field(name="Theme", value="Not set", inline=False)

        await inter.edit_original_message(embed=embed)


def setup(bot: commands.InteractionBot) -> None:
    bot.add_cog(Info(bot))

