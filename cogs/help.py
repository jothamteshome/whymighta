import logging

import disnake
from disnake.ext import commands

from views.help import HelpView, build_catalog, overview_embed

logger = logging.getLogger(__name__)


class Help(commands.Cog):
    def __init__(self, bot: commands.InteractionBot) -> None:
        self.bot: commands.InteractionBot = bot

    @commands.slash_command(description="Browse all bot commands")
    async def help(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()
        catalog = build_catalog(self.bot, in_dm=inter.guild_id is None)
        view = HelpView(catalog)
        await inter.edit_original_response(embed=overview_embed(catalog), view=view)
        view.message = await inter.original_message()


def setup(bot: commands.InteractionBot) -> None:
    bot.add_cog(Help(bot))
