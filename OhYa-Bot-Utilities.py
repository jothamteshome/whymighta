import disnake
import time

from disnake.ext import commands


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, message):
        before = time.monotonic()
        embed = disnake.Embed(title=":information_source: | Pong!", description="\n", color=0x9534eb)
        message = await message.channel.send(embed=embed)
        latency = (time.monotonic() - before) * 1000
        embed.add_field(name="Latency", value=str(int(latency)) + "ms", inline=False)
        embed.add_field(name="API", value=str(int(self.bot.latency * 1000)) + "ms", inline=False)
        await message.edit(embed=embed)

    async def utilities_message(self, message):
        if self.bot.command_prefix + "ping" in message.content:
            await self.ping(message)


def setup(bot):
    bot.add_cog(Utilities(bot))
