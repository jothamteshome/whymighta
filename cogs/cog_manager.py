import logging
import os

import disnake
from disnake import ApplicationCommandInteraction, Embed
from disnake.ext import commands
from utils.constants import DEFAULT_EMBED_COLOR

logger = logging.getLogger(__name__)


class CogManager(commands.Cog):
    def __init__(self, bot: commands.InteractionBot) -> None:
        self.bot: commands.InteractionBot = bot

    @commands.slash_command(description="Manage cogs (bot owner only)", contexts=disnake.InteractionContextTypes(guild=True))
    @commands.is_owner()
    async def cog(self, inter: ApplicationCommandInteraction):
        pass

    @cog.sub_command(description="List available cogs")
    async def list(self, inter: ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        embed = Embed()

        embed = Embed(title="Available Cogs", description=f"\n{'-' * 25}", color=DEFAULT_EMBED_COLOR)          

        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                name, ext = os.path.splitext(filename)

                if name == "cog_manager":
                    continue

                embed.add_field(name=f"• {name}", value="", inline=False)


        await inter.edit_original_message(embed=embed)


    @cog.sub_command(description="Load a cog")
    async def load(
        self, inter: ApplicationCommandInteraction,
        name: str = commands.Param(description="Name of the cog (e.g., games)")
    ):
        await inter.response.defer(ephemeral=True)

        try:
            self.bot.load_extension(f"cogs.{name}")
            await inter.edit_original_message(f"Loaded `cogs.{name}`")
        except Exception as e:
            await inter.edit_original_message(f"Failed to load cog: {e}")


    @cog.sub_command(description="Unload a cog")
    async def unload(
        self, inter: ApplicationCommandInteraction,
        name: str = commands.Param(description="Name of the cog (e.g., games)")
    ):
        await inter.response.defer(ephemeral=True)

        if name.lower() == "cog_manager":
            await inter.edit_original_message("You cannot unload the cog manager itself.")
            return

        try:
            self.bot.unload_extension(f"cogs.{name}")
            await inter.edit_original_message(f"Unloaded `cogs.{name}`")
        except Exception as e:
            await inter.edit_original_message(f"Failed to unload cog: {e}")


    @cog.sub_command(description="Reload a cog")
    async def reload(
        self, inter: ApplicationCommandInteraction,
        name: str = commands.Param(description="Name of the cog (e.g., games)")
    ):
        await inter.response.defer(ephemeral=True)

        if name.lower() == "cog_manager":
            await inter.edit_original_message("You cannot reload the cog manager itself.")
            return
        
        try:
            self.bot.reload_extension(f"cogs.{name}")
            await inter.edit_original_message(f"Reloaded `cogs.{name}`")
        except Exception as e:
            await inter.edit_original_message(f"Failed to reload cog: {e}")


def setup(bot: commands.InteractionBot) -> None:
    bot.add_cog(CogManager(bot))