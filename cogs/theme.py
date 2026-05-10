import asyncio
import json
import logging
import random
from io import BytesIO, StringIO
from typing import Optional

import disnake
from disnake.ext import commands
from pydantic import ValidationError

from database.manager import Database
from models.theme import GuildTheme

logger = logging.getLogger(__name__)


class Theme(commands.Cog):
    def __init__(self, bot: commands.InteractionBot) -> None:
        self.bot: commands.InteractionBot = bot
        self.database: Database = bot.db

    @commands.slash_command(
        default_member_permissions=disnake.Permissions(administrator=True)
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

        new_nicks = list(theme.names)
        random.shuffle(new_nicks)

        skipped: list[tuple[str, str]] = []

        for member in members:
            new_nick = new_nicks.pop()

            if member != inter.guild.me and (member == inter.guild.owner or inter.guild.me.top_role <= member.top_role):
                logger.debug("Skipping %s (role hierarchy)", member.name)
                skipped.append((member.name, new_nick))
                continue

            try:
                await member.edit(nick=new_nick)
                logger.debug("Assigned %s -> %s", member.name, new_nick)
                await asyncio.sleep(1.1)
            except disnake.errors.Forbidden as e:
                logger.debug("No permission for %s: %s", member.name, e)
                skipped.append((member.name, new_nick))
            except disnake.errors.HTTPException as e:
                logger.warning("HTTP Error for %s: %s %s", member.name, e.status, e.text)
                skipped.append((member.name, new_nick))

        await inter.edit_original_message("Random nicknames have been assigned")

        if skipped:
            lines = "\n".join(f"`{name}` — {nick}" for name, nick in skipped)
            await inter.channel.send(f"**Could not assign nicknames for:**\n{lines}")

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

        with StringIO() as string_fp:
            json.dump(server_names, string_fp)
            string_fp.seek(0)
            byte_fp = BytesIO(string_fp.read().encode("utf-8"))
            server_names_file = disnake.File(fp=byte_fp, filename="server_nicknames_dump.json")

        await inter.edit_original_response(content="", file=server_names_file)

    @theme.sub_command(description="Show the current theme details")
    async def show(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()

        raw_theme = await self.database.get_theme(inter.guild.id)
        if not raw_theme:
            await inter.edit_original_message("No theme is currently set.")
            return

        theme = GuildTheme.model_validate(raw_theme)
        bot_nick = inter.guild.me.nick or "None assigned"

        embed = disnake.Embed(title="Current Theme", color=0x9534eb)
        embed.add_field(name="Theme Title", value=theme.title or "Not set", inline=False)
        embed.add_field(name="Description", value=(theme.description or "Not set")[:100], inline=False)
        embed.add_field(name="Names in Pool", value=str(len(theme.names)), inline=True)
        embed.add_field(name="Roleplay", value="On" if theme.roleplay else "Off", inline=True)
        embed.add_field(name="Bot's Character", value=bot_nick, inline=True)

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
        raw_theme = await self.database.get_theme(inter.guild.id)
        if not raw_theme:
            await inter.edit_original_message("No theme is currently set.")
            return
        theme = GuildTheme.model_validate(raw_theme)
        updated = theme.model_copy(update={"roleplay": enabled == "on"})
        await self.database.set_theme(inter.guild.id, updated.model_dump())
        status = "enabled" if updated.roleplay else "disabled"
        await inter.edit_original_message(f"Roleplay is now {status}.")


def setup(bot: commands.InteractionBot) -> None:
    bot.add_cog(Theme(bot))
