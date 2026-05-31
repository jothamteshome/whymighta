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
        await inter.response.defer(ephemeral=True)
        is_admin = (
            inter.guild_id is not None
            and inter.author.guild_permissions.administrator
        )
        catalog = build_catalog(self.bot, in_dm=inter.guild_id is None, is_admin=is_admin)
        view = HelpView(self.bot, catalog)
        await inter.edit_original_response(embed=overview_embed(self.bot, catalog), view=view)
        view.message = await inter.original_message()


def setup(bot: commands.InteractionBot) -> None:
    bot.add_cog(Help(bot))
