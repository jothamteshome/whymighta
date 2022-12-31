import disnake
import PropertiesReader
import time
import whymightaGlobalVariables
import whymightaUtilities
import whymightaHelp

from whymightaApex import ApexHandler
from whymightaOpenWeatherMap import OpenWeatherHandler
from whymightaReddit import RedditHandler
from whymightaTheList import TheListHandler

# Initialize reader for properties file
prop_reader = PropertiesReader.PropertiesReader()

# Load bot token from a file
TOKEN = prop_reader.get_key('DISCORD_TOKEN')

@whymightaGlobalVariables.bot.event
async def on_ready():
    print("Logged in as {0.user}".format(whymightaGlobalVariables.bot))


@whymightaGlobalVariables.bot.event
async def on_message(message):
    channel = message.channel
    if message.author.bot is not True:
        if message.content == whymightaGlobalVariables.bot.command_prefix:
            await channel.send("Please check j!help for available functions")
        if whymightaGlobalVariables.bot.command_prefix + "weather" in message.content:
            await OpenWeatherHandler(whymightaGlobalVariables.bot).weather_message(message)
        elif whymightaGlobalVariables.bot.command_prefix + "reddit" in message.content:
            await RedditHandler(whymightaGlobalVariables.bot).on_reddit_message(message)
        elif whymightaGlobalVariables.bot.command_prefix + "the_list" in message.content:
            await TheListHandler(whymightaGlobalVariables.bot).on_list_message(message)
        elif whymightaGlobalVariables.bot.command_prefix + "apex" in message.content:
            await ApexHandler(whymightaGlobalVariables.bot).apex_message(message)


whymightaGlobalVariables.bot.run(TOKEN)
