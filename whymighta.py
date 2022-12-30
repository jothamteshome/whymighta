import disnake
import PropertiesReader
import time

from whymightaApex import ApexHandler
from whymightaHelp import HelpHandler
from whymightaOpenWeatherMap import OpenWeatherHandler
from whymightaReddit import RedditHandler
from whymightaTheList import TheListHandler
from whymightaUtilities import Utilities

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
            await Utilities(bot).utilities_message(message)
        elif bot.command_prefix + "help" in message.content:
            await HelpHandler(bot).help(message=message)
        elif bot.command_prefix + "weather" in message.content:
            await OpenWeatherHandler(bot).weather_message(message)
        elif bot.command_prefix + "reddit" in message.content:
            await RedditHandler(bot).on_reddit_message(message)
        elif bot.command_prefix + "the_list" in message.content:
            await TheListHandler(bot).on_list_message(message)
        elif bot.command_prefix + "apex" in message.content:
            await ApexHandler(bot).apex_message(message)


bot.run(TOKEN)
