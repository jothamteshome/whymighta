import discord
from discord.ext import commands


class HelpHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='OhYa_help')
    async def help(self, message):
        channel = message.channel
        user_message = message.content
        user_message = user_message.replace(self.bot.command_prefix + "help", "")
        user_message = user_message.split()
        embed = None
        if len(user_message) == 0:
            embed = discord.Embed(title=":information_source: | OhYa Bot Help Menu", color=0x9534eb)
            embed.add_field(name="-" * 50, value="`weather` `reddit` `clear` `ping`", inline=False)

            embed.set_footer(text="Use j!help [command] for more information")

        elif len(user_message) == 1:
            user_message = user_message[0].lower()
            if user_message == "weather":
                embed = discord.Embed(title="Weather", description="**`usage`** - j!weather [city] [state-code] ["
                                                                   "country-code] [unit-type]", color=0x9534eb)
                embed.add_field(name="-" * 95, value="**`city`** - Type in a city name. Use '-' in place of "
                                                     "spaces\n\n**`state-code`** - (Optional) Name or code of a state. "
                                                     "Only works in the US\n\n**`country-code`** - (Optional) Name or "
                                                     "code of a country\n\n**`unit-type`** - Type in units you would "
                                                     "like to use. Select from `Imperial, Metric, or Standard`")

            elif user_message == "reddit":
                embed = discord.Embed(title="Reddit", description="**`usage`** - j!reddit [subreddit] [sort_type] ["
                                                                  "top_sort] [num_posts]", color=0x9534eb)
                embed.add_field(name="-" * 95, value="**`subreddit`** - Enter the name of the subreddit you would "
                                                     "like to visit\n\n **`sort_type`** - Reddit sorting condition "
                                                     "you would like. Select from `Hot, New, Rising, "
                                                     "or Top`\n\n**`top_sort`** - Only applies if sort type is 'Top'. "
                                                     "Choose the timespan you would like to sort by. Select from "
                                                     "`Now, Day, Week, Month, Year, or All`\n\n**`num_posts`** - "
                                                     "Number of posts you would like to see. Select a number "
                                                     "including and between 2 and 10")

            elif user_message == "clear":
                embed = discord.Embed(title="Clear", description="**`usage`** - j!clear [num_posts]", color=0x9534eb)
                embed.add_field(name="-" * 95, value="**`num_posts`** - (Optional) Select a number of posts to delete "
                                                     "between and including 1 and 100. Defaults to 5")

            elif user_message == "ping":
                embed = discord.Embed(title="Ping", description="**`usage`** - j!ping", color=0x9534eb)
            else:
                await channel.send("Please select a valid function.")
        elif len(user_message) > 1:
            await channel.send("Please select a valid function.")

        if embed is not None:
            await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(HelpHandler(bot))
