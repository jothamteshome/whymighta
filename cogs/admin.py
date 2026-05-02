import logging

import disnake
from disnake.ext import commands

from utils.admin_utils import clear_guild_commands

logger = logging.getLogger(__name__)


class Admin(commands.Cog):
    def __init__(self, bot: commands.InteractionBot) -> None:
        self.bot: commands.InteractionBot = bot

    @commands.slash_command()
    @commands.is_owner()
    async def admin(self, inter: disnake.ApplicationCommandInteraction) -> None:
        pass

    @admin.sub_command(description="Clears all guild application commands")
    async def clear_commands(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer(ephemeral=True)
        guilds = await clear_guild_commands(self.bot)

        embed = disnake.Embed(title="Guilds Cleared", description=f"\n{'-' * 25}", color=0x9534eb)
        for guild in guilds:
            embed.add_field(name=f"• {guild.id} - {guild.name}", value="", inline=False)

        await inter.edit_original_message(embed=embed)


def setup(bot: commands.InteractionBot) -> None:
    bot.add_cog(Admin(bot))
