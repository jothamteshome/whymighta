import json
import logging
from io import BytesIO, StringIO
from typing import Optional

import disnake
from disnake.ext import commands
from pydantic import ValidationError

from database.manager import Database
from models.theme import GuildTheme
from utils.theme_utils import (
    add_theme_fields,
    apply_guild_appearance,
    assign_nicknames,
    get_guild_theme,
)

logger = logging.getLogger(__name__)


class Theme(commands.Cog):
    def __init__(self, bot: commands.InteractionBot) -> None:
        self.bot: commands.InteractionBot = bot
        self.database: Database = bot.db

    @commands.slash_command(
        default_member_permissions=disnake.Permissions(administrator=True),
        contexts=disnake.InteractionContextTypes(guild=True),
    )
    async def theme(self, inter: disnake.ApplicationCommandInteraction) -> None:
        pass

    @theme.sub_command(description="Randomly updates server nicknames based on those found in uploaded file")
    async def apply(self, inter: disnake.ApplicationCommandInteraction, file: disnake.Attachment) -> None:
        await inter.response.defer()

        if "application/json" not in file.content_type:
            await inter.edit_original_message("File must be a json")
            return

        fp = BytesIO()
        logger.debug("Starting file download")
        await file.save(fp)
        fp.seek(0)

        try:
            theme = GuildTheme.model_validate(json.load(fp))
        except json.JSONDecodeError:
            await inter.edit_original_message("Could not parse file: invalid JSON.")
            return
        except ValidationError as e:
            await inter.edit_original_message(f"Invalid theme format: {e}")
            return

        members = inter.guild.members

        if len(theme.names) < len(members):
            await inter.edit_original_message(
                f"Please provide enough names to allocate one for each member in server "
                f"({len(members) - len(theme.names)} more required)"
            )
            return

        logger.debug("JSON loaded: %d names, %d members", len(theme.names), len(members))

        skipped = await assign_nicknames(inter.guild, theme.names)

        await inter.edit_original_message("Random nicknames have been assigned")

        if skipped:
            lines = "\n".join(f"`{name}` — {nick}" for name, nick in skipped)
            await inter.channel.send(f"**Could not assign nicknames for:**\n{lines}")

        appearance_feedback = await apply_guild_appearance(inter.guild, theme)
        for message in appearance_feedback:
            await inter.channel.send(message)

        try:
            await self.database.set_theme(inter.guild.id, theme.model_dump())
        except Exception as e:
            logger.error("Failed to save theme for guild %d: %s", inter.guild.id, e)
            await inter.channel.send("Nicknames were assigned but the theme could not be saved to the database.")

    @theme.sub_command(description="Get current server nicknames in json format")
    async def export(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()

        server_names: dict[str, Optional[str]] = {
            member.name: member.nick for member in inter.guild.members
        }

        byte_fp = BytesIO(json.dumps(server_names).encode())
        server_names_file = disnake.File(fp=byte_fp, filename="server_nicknames_dump.json")

        await inter.edit_original_response(content="", file=server_names_file)

    @theme.sub_command(description="Show the current theme details")
    async def show(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()

        theme = await get_guild_theme(self.database, inter.guild.id)
        if not theme:
            await inter.edit_original_message("No theme is currently set.")
            return

        bot_nick = inter.guild.me.nick or "None assigned"

        embed = disnake.Embed(title="Current Theme", color=0x9534eb)
        add_theme_fields(embed, theme, bot_nick)

        await inter.edit_original_message(embed=embed)

    @theme.sub_command(description="Clear the current theme")
    async def clear(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()
        await self.database.clear_theme(inter.guild.id)
        await inter.edit_original_message(
            "Theme cleared. New members will need to be renamed manually until a new theme is applied."
        )

    @theme.sub_command(description="Toggle roleplay mode for the current theme")
    async def roleplay(
        self,
        inter: disnake.ApplicationCommandInteraction,
        enabled: str = commands.Param(choices=["on", "off"]),
    ) -> None:
        await inter.response.defer()

        theme = await get_guild_theme(self.database, inter.guild.id)
        if not theme:
            await inter.edit_original_message("No theme is currently set.")
            return

        updated = theme.model_copy(update={"roleplay": enabled == "on"})
        await self.database.set_theme(inter.guild.id, updated.model_dump())
        status = "enabled" if updated.roleplay else "disabled"
        await inter.edit_original_message(f"Roleplay is now {status}.")


def setup(bot: commands.InteractionBot) -> None:
    bot.add_cog(Theme(bot))

