import math
import time
from disnake import Embed
from disnake.ext import commands
from utils.database import Database
from utils.helpers import Helpers


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = Database()
        self.helpers = Helpers(self.bot)


    @commands.slash_command()
    async def utilities(self, inter):
        pass


    @utilities.sub_command(
        description="Check the latency of the whymighta")
    async def ping(self, inter):
        before = time.monotonic()
        embed = Embed(title=":information_source: | Pong!", description="\n", color=0x9534eb)
        await inter.response.send_message(embed=embed)
        latency = (time.monotonic() - before) * 1000
        embed.add_field(name="Latency", value=str(int(latency)) + "ms", inline=False)
        embed.add_field(name="API", value=str(int(self.bot.latency * 1000)) + "ms", inline=False)
        await inter.edit_original_response(embed=embed)


    @utilities.sub_command(
        description="Checks the level of a user")
    async def level(self, inter):
        await inter.response.defer()

        curr_xp = await self.database.current_user_score(inter.author.id, inter.guild_id)
        curr_level = self.helpers.check_level(curr_xp)

        curr_level_split = str(curr_level).split(".")

        next_level_progress = int(round(curr_level - int(curr_level_split[0]), 2) * 100)

        progress_bar = math.floor(next_level_progress / 10)

        embed = Embed(title=f"{inter.author.name}'s Level Progress", description="\n", color=0x9534eb)
        embed.add_field(name=f"{next_level_progress}% to Level {int(curr_level_split[0]) + 1}",
                        value=(progress_bar * "🔵") + ((10 - progress_bar) * "⚪"), inline=False)

        await inter.edit_original_message(embed=embed)


    @utilities.sub_command(
        description="Puts a deserving criminal behind bars")
    async def jail(self, inter, name):
        members = {member.name: member for member in inter.guild.members}
        nicknames = {member.nick: member for member in inter.guild.members}

        if name in members:
            await inter.response.send_message("Generating Image...")
            jailed_image = self.helpers.imprison_member(members[name])
            await inter.edit_original_response(content="", file=jailed_image)
        elif name in nicknames:
            await inter.response.send_message("Generating Image...")
            jailed_image = self.helpers.imprison_member(nicknames[name])
            await inter.edit_original_response(content="", file=jailed_image)
        else:
            await inter.response.send_message("User does not exist. Please try again with the user's discord name")


def setup(bot):
    bot.add_cog(Utilities(bot))