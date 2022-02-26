import discord
from discord.ext import commands


class HelpHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='OhYa_help')
    async def help(self, message):
        channel = message.channel
        embed = discord.Embed(title=":information_source: | OhYa Bot Help Menu", description='-' * 95, color=0x9534eb)
        embed.add_field(name="Weather\n", value="**`usage`** - j!weather [city] [state-code] [country-code] ["
                                                "unit-type]\n\n "
                                                "`city` - Type in a city name. Use '-' in place of spaces\n\n"
                                                "`state-code` - (Optional) Name or code of a state. Only works in the "
                                                "US\n\n "
                                                "`country-code` - (Optional) Name or code of a country\n\n"
                                                "`unit-type` - Type in units you would like to use. "
                                                "\nSelect from: | imperial | metric | standard |"
                                                + "\n\n" + "-" * 95, inline=False)

        embed.add_field(name="Reddit\n",
                        value="**`usage`** - j!reddit [subreddit] [sort_type] [top_sort] [num_posts]\n\n"
                              "`subreddit` - Enter the name of the subreddit you would like to visit\n\n"
                              "`sort_type` - Reddit sorting condition you would like. \nSelect from: | "
                              "Hot | New | Rising | Top |\n\n"
                              "`top_sort` - Only applies if sort type is 'Top'. Choose the timespan "
                              "you would like to sort by. \nSelect from: | Now | Day | Week | Month | "
                              "Year | All |\n\n"
                              "`num_posts` - Number of posts you would like to see. Select a number "
                              "including and between 2 and 10" + "\n\n" + "-" * 95, inline=False)

        embed.add_field(name="Clear\n", value="**`usage`** - j!clear [num_posts]\n\n"
                                              "`num_posts` - (Optional) Select a number of posts to delete. Defaults "
                                              "to 5 and maximum is 100\n\n" + "-" * 95, inline=False)
        embed.add_field(name="Ping\n", value="**`usage`** - j!ping\n\n Returns bot latency\n\n" + "-" * 95, inline=False)

        embed.set_footer(text="For more information and help contact ohyabotdev@gmail.com")
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(HelpHandler(bot))
