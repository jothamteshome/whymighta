import disnake
import PropertiesReader
import time

from disnake.ext import commands

# Initialize reader for properties file
prop_reader = PropertiesReader.PropertiesReader()

# Load bot token from a file
TOKEN = prop_reader.get_key('DISCORD_TOKEN')

intents = disnake.Intents.all()

# Instantiate a Discord client
bot = disnake.ext.commands.Bot(command_prefix='j!', intents=intents)


@bot.event
async def on_ready():
    bot.load_extension("OhYa-Bot-OpenWeatherMap")
    bot.load_extension("OhYa-Bot-Reddit")
    bot.load_extension("OhYa-Bot-Help")
    bot.load_extension("OhYa-Bot-TheList")
    bot.load_extension("OhYa-Bot-Apex")
    bot.load_extension("OhYa-Bot-Utilities")
    print("Logged in as {0.user}".format(bot))


@bot.event
async def on_message(message):
    channel = message.channel
    utilities = {"ping", "clear"}
    if message.author.bot is not True:
        if message.content == bot.command_prefix:
            await channel.send("Please check j!help for available functions")
        check_util = message.content.replace(bot.command_prefix, "")
        check_util = check_util.split()
        if check_util[0] in utilities:
            utilities_cog = bot.get_cog("Utilities")
            await utilities_cog.utilities_message(message)
        elif bot.command_prefix + "help" in message.content:
            help_cog = bot.get_cog('HelpHandler')
            await help_cog.help(message)
        elif bot.command_prefix + "weather" in message.content:
            weather_cog = bot.get_cog('OpenWeatherHandler')
            await weather_cog.weather_message(message)
        elif bot.command_prefix + "reddit" in message.content:
            reddit_cog = bot.get_cog('RedditHandler')
            await reddit_cog.on_reddit_message(message)
        elif bot.command_prefix + "the_list" in message.content:
            the_list_cog = bot.get_cog('TheListHandler')
            await the_list_cog.on_list_message(message)
        elif bot.command_prefix + "apex" in message.content:
            apex_cog = bot.get_cog('ApexHandler')
            await apex_cog.apex_message(message)


bot.run(TOKEN)
