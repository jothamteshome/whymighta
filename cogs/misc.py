import logging

import disnake
from disnake.ext import commands

from utils.image_utils import imprison_member

logger = logging.getLogger(__name__)


class Misc(commands.Cog):
    category_display_name = "Misc"
    category_emoji = "🎲"

    def __init__(self, bot: commands.InteractionBot) -> None:
        self.bot: commands.InteractionBot = bot

    @commands.slash_command(
        description="Puts a deserving criminal behind bars",
        contexts=disnake.InteractionContextTypes(guild=True),
    )
    async def jail(self, inter: disnake.ApplicationCommandInteraction, name: str) -> None:
        members = {member.name: member for member in inter.guild.members}
        nicknames = {member.nick: member for member in inter.guild.members if member.nick}

        member = members.get(name) or nicknames.get(name)

        if member is None:
            await inter.response.send_message(
                "User does not exist. Please try again with the user's discord name"
            )
            return

        await inter.response.send_message("Generating Image...")
        jailed_image = await imprison_member(member)
        await inter.edit_original_response(content="", file=jailed_image)


def setup(bot: commands.InteractionBot) -> None:
    bot.add_cog(Misc(bot))
