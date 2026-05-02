import logging
import math
import time

from disnake import ApplicationCommandInteraction, Embed
from disnake.ext import commands

from database.manager import Database
from utils import xp
from utils.image_utils import imprison_member

logger = logging.getLogger(__name__)


class Utilities(commands.Cog):
    def __init__(self, bot: commands.InteractionBot) -> None:
        self.bot: commands.InteractionBot = bot
        self.database: Database = bot.db

    @commands.slash_command(description="Check the latency of the bot")
    async def ping(self, inter: ApplicationCommandInteraction) -> None:
        before = time.monotonic()
        embed = Embed(title=":information_source: | Pong!", description="\n", color=0x9534eb)
        await inter.response.send_message(embed=embed)
        latency = (time.monotonic() - before) * 1000
        embed.add_field(name="Latency", value=str(int(latency)) + "ms", inline=False)
        embed.add_field(name="API", value=str(int(self.bot.latency * 1000)) + "ms", inline=False)
        await inter.edit_original_response(embed=embed)

    @commands.slash_command(description="Checks the level of a user")
    async def level(self, inter: ApplicationCommandInteraction) -> None:
        await inter.response.defer()

        curr_xp = await self.database.current_user_score(inter.author.id, inter.guild_id)
        curr_level = xp.check_level(curr_xp)

        curr_level_floor = math.floor(curr_level)
        next_level_progress = int(round(curr_level - curr_level_floor, 2) * 100)
        progress_bar = math.floor(next_level_progress / 10)

        embed = Embed(title=f"{inter.author.name}'s Level Progress", description="\n", color=0x9534eb)
        embed.add_field(
            name=f"{next_level_progress}% to Level {curr_level_floor + 1}",
            value=(progress_bar * "🔵") + ((10 - progress_bar) * "⚪"),
            inline=False,
        )

        await inter.edit_original_message(embed=embed)

    @commands.slash_command(description="Puts a deserving criminal behind bars")
    async def jail(self, inter: ApplicationCommandInteraction, name: str) -> None:
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
    bot.add_cog(Utilities(bot))