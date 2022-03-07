import PropertiesReader

from disnake.ext import commands
from aiohttp import ClientSession

prop_reader = PropertiesReader.PropertiesReader()


class ApexHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='Apex')
    async def apex_stats(self, channel, player, platform, mode):
        pass

    @commands.command(name='Apex Message')
    async def apex_message(self, message):
        check_help = False
        channel = message.channel
        user_message = message.content
        user_message = user_message.replace(self.bot.command_prefix + "apex", "")
        user_message = user_message.split()
        # Parameters are player name, platform, and mode
        await self.apex_stats(1,2,3,4)


def setup(bot):
    bot.add_cog(ApexHandler(bot))
