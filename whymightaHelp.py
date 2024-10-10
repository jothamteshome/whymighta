import disnake
import whymightaGlobalVariables

@whymightaGlobalVariables.bot.slash_command(
    description="Descriptions of bot commands")
async def commands(inter, command: str = "", subcommand: str = ""):
    embed = None
    if command == "":
        embed = disnake.Embed(title=":information_source: | whymighta Help Menu", color=0x9534eb)
        embed.add_field(name="\u200b", value="\n\n**Main Commands**\n" + "-" * 50 + "\n`weather` `reddit` `apex`"
                                                                                    "\n\n**Utility Commands**\n" + "-" * 50 + "\n`clear` `ping`"
                                                                                                                              "\n\n**Other**\n" + "-" * 50 + "\n`the_list`",
                        inline=False)

    elif command == "weather":
        embed = disnake.Embed(title="Weather", description="**`usage`** - j!weather [city] [state-code] ["
                                                           "country-code] [unit-type]", color=0x9534eb)
        embed.add_field(name="-" * 80, value="**`city`** - Type in a city name. Use '-' in place of "
                                             "spaces\n\n**`state-code`** - (Optional) Name or code of a state. "
                                             "Only works in the US\n\n**`country-code`** - (Optional) Name or "
                                             "code of a country\n\n**`unit-type`** - Type in units you would "
                                             "like to use. Select from `Imperial, Metric, or Standard`")

    elif command == "reddit":
        embed = disnake.Embed(title="Reddit", description="**`usage`** - j!reddit [subreddit] [sort_type] ["
                                                          "top_sort] [num_posts]", color=0x9534eb)
        embed.add_field(name="-" * 80, value="**`subreddit`** - Enter the name of the subreddit you would "
                                             "like to visit\n\n **`sort_type`** - Reddit sorting condition "
                                             "you would like. Select from `Hot, New, Rising, "
                                             "or Top`\n\n**`top_sort`** - Only applies if sort type is 'Top'. "
                                             "Choose the timespan you would like to sort by. Select from "
                                             "`Now, Day, Week, Month, Year, or All`\n\n**`num_posts`** - "
                                             "Number of posts you would like to see. Select a number "
                                             "including and between 2 and 10")

    elif command == "clear":
        embed = disnake.Embed(title="Clear", description="**`usage`** - j!clear [num_posts]", color=0x9534eb)
        embed.add_field(name="-" * 80, value="**`num_posts`** - (Optional) Select a number of posts to delete "
                                             "between and including 1 and 100. Defaults to 5")

    elif command == "ping":
        embed = disnake.Embed(title="Ping", description="**`usage`** - j!ping", color=0x9534eb)

    elif command == "the_list":
        embed = disnake.Embed(title="The List", description="**`usage`** - j!the_list [action] [person]",
                              color=0x9534eb)
        embed.add_field(name="-" * 80, value="**`action`** - Select which mode to use with this function. "
                                             "Select from `Add`, `Remove`, and `View`\n\n**`person`** - "
                                             "Select a person to add or remove from the list")
    elif command == "apex" and subcommand == "":
        embed = disnake.Embed(title="Apex Functions", color=0x9534eb)
        embed.add_field("-" * 60, value="**`stats`** - Retrieve the stats of a player\n\n**`map`** - Check "
                                        "the current map rotation")
        embed.set_footer(text="Use j!help apex [command] to see how to use the following functions")

    elif command == "apex" and subcommand == "stats":
        embed = disnake.Embed(title="Apex Stats", description="**`usage`** - j!apex stats [player] [platform]",
                              color=0x9534eb)
        embed.add_field(name="-" * 80, value="**`player`** - Select a person to their Apex Legends "
                                             "stats\n\n**`platform`** - Select the platform the user plays "
                                             "on. Select from `PC`, `PS4`, and `X1`")

    elif command == "apex" and subcommand == "map":
        embed = disnake.Embed(title="Apex Map Rotation", description="**`usage`** - j!apex map",
                              color=0x9534eb)

    if embed is not None:
        await inter.response.send_message(embed=embed)

