import logging
from typing import Optional

import disnake
from disnake.ext import commands

from database.manager import Database

logger = logging.getLogger(__name__)


class ServerConfig(commands.Cog):
    def __init__(self, bot: commands.InteractionBot) -> None:
        self.bot: commands.InteractionBot = bot
        self.database: Database = bot.db

    # ---- /bot_channel ----

    @commands.slash_command(
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def bot_channel(self, inter: disnake.ApplicationCommandInteraction) -> None:
        pass

    @bot_channel.sub_command(description="Set a new channel as the default bot channel")
    async def use(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()
        await self.database.set_bot_text_channel_id(inter.guild.id, inter.channel.id)
        await inter.edit_original_message(f"Bot messages will now appear in {inter.channel.name}!")

    @bot_channel.sub_command(description="Get name of current bot channel")
    async def show(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()

        bot_channel_id = await self.database.get_bot_text_channel_id(inter.guild.id)
        bot_channel: Optional[str] = None

        for channel in inter.guild.text_channels:
            if channel.id == bot_channel_id:
                bot_channel = channel.name
                break

        if bot_channel is not None:
            await inter.edit_original_message(f"Current bot text channel is #{bot_channel}")
        else:
            await inter.edit_original_message("No channel has been set as the bot channel")

    # ---- /toggle ----

    @commands.slash_command(
        default_member_permissions=disnake.Permissions(administrator=True)
    )
    async def toggle(self, inter: disnake.ApplicationCommandInteraction) -> None:
        pass

    @toggle.sub_command(description="Toggles the mock status of the bot")
    async def mock(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()
        if await self.database.toggle_mock(inter.guild_id):
            await inter.edit_original_message("Mocking has been enabled")
        else:
            await inter.edit_original_message("Mocking has been disabled")

    @toggle.sub_command(description="Toggles the binary writing status of the bot")
    async def binary(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()
        if await self.database.toggle_binary(inter.guild_id):
            await inter.edit_original_message("Binary has been enabled")
        else:
            await inter.edit_original_message("Binary has been disabled")


def setup(bot: commands.InteractionBot) -> None:
    bot.add_cog(ServerConfig(bot))
