from disnake.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @commands.slash_command(
            description="Descriptions of bot commands"
    )
    async def help(self, inter):
        await inter.response.send_message("WIP")


def setup(bot):
    bot.add_cog(Help(bot))


# @help.sub_command()
# async def commands(inter):
#     embed = disnake.Embed(title=":information_source: | whymighta Help Menu", color=0x9534eb)
#     embed.add_field(name="\u200b", value="\n\n**Main Commands**\n" + "-" * 50 + "\n`weather` `reddit` `apex`"
#                                                                                 "\n\n**Utility Commands**\n" + "-" * 50 + "\n`clear` `ping`"
#                                                                                                                             "\n\n**Other**\n" + "-" * 50 + "\n`the_list`",
#                     inline=False)
    
#     await inter.response.send_message(embed=embed)


# @help.sub_command(description="Display information about the weather command")
# async def weather(inter):
#     embed = disnake.Embed(title="Weather", description="**`usage`** - j!weather [city] [state-code] ["
#                                                            "country-code] [unit-type]", color=0x9534eb)
#     embed.add_field(name="-" * 80, value="**`city`** - Type in a city name. Use '-' in place of "
#                                             "spaces\n\n**`state-code`** - (Optional) Name or code of a state. "
#                                             "Only works in the US\n\n**`country-code`** - (Optional) Name or "
#                                             "code of a country\n\n**`unit-type`** - Type in units you would "
#                                             "like to use. Select from `Imperial, Metric, or Standard`")
    
#     await inter.response.send_message(embed=embed)    


# @help.sub_command()
# async def clear(inter):
#     embed = disnake.Embed(title="Clear", description="**`usage`** - j!clear [num_posts]", color=0x9534eb)
#     embed.add_field(name="-" * 80, value="**`num_posts`** - (Optional) Select a number of posts to delete "
#                                              "between and including 1 and 100. Defaults to 5")
    
#     await inter.response.send_message(embed=embed)


# @help.sub_command()
# async def ping(inter):
#     embed = disnake.Embed(title="Ping", description="**`usage`** - j!ping", color=0x9534eb)

#     await inter.response.send_message(embed=embed)