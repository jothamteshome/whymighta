import asyncio
import json
import logging
import random
from io import BytesIO, StringIO
from typing import Optional

import disnake
from disnake.ext import commands

logger = logging.getLogger(__name__)


class Theme(commands.Cog):
    def __init__(self, bot: commands.InteractionBot) -> None:
        self.bot: commands.InteractionBot = bot

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
        server_structure = json.load(fp)

        if "names" not in server_structure:
            await inter.edit_original_message("Please make sure `names` key exists in JSON")
            return
        elif not isinstance(server_structure["names"], list):
            await inter.edit_original_message("Please make sure the value of `names` is a list")
            return

        members = inter.guild.members

        if len(server_structure["names"]) < len(members):
            await inter.edit_original_message(
                f"Please provide enough names to allocate one for each member in server "
                f"({len(members) - len(server_structure['names'])} more required)"
            )
            return

        logger.debug("JSON loaded: %d names, %d members", len(server_structure["names"]), len(members))

        new_nicks = server_structure["names"]
        random.shuffle(new_nicks)

        skipped: list[tuple[str, str]] = []

        for member in members:
            new_nick = new_nicks.pop()

            if not member.bot and (
                member == inter.guild.owner or inter.guild.me.top_role <= member.top_role
            ):
                logger.debug("Skipping %s (role hierarchy)", member.name)
                skipped.append((member.name, new_nick))
                continue

            try:
                await asyncio.wait_for(member.edit(nick=new_nick), timeout=10)
                logger.debug("Assigned %s -> %s", member.name, new_nick)
                await asyncio.sleep(0.5)
            except disnake.errors.Forbidden as e:
                logger.debug("Could not set nick for %s (no permission): %s", member.name, e)
                skipped.append((member.name, new_nick))
            except (asyncio.TimeoutError, disnake.errors.HTTPException) as e:
                logger.warning("Could not set nick for %s: %s", member.name, e)
                skipped.append((member.name, new_nick))

        await inter.edit_original_message("Random nicknames have been assigned")

        if skipped:
            lines = "\n".join(f"`{name}` — {nick}" for name, nick in skipped)
            await inter.channel.send(f"**Could not assign nicknames for:**\n{lines}")

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


def setup(bot: commands.InteractionBot) -> None:
    bot.add_cog(Theme(bot))
