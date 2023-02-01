import disnake
import whymightaDatabase
import whymightaGlobalVariables
import whymightaUtilities
import whymightaHelp
import whymightaOpenWeatherMap
import whymightaBirthdays

from whymightaApex import ApexHandler
from whymightaReddit import RedditHandler


# Retrieve bot token from database
TOKEN = whymightaDatabase.getKey('DISCORD_TOKEN')


@whymightaGlobalVariables.bot.event
async def on_ready():
    whymightaBirthdays.birthdayCheck.start()
    whymightaGlobalVariables.guild_ids = [int(guild['guild_id'])
                                          for guild in whymightaDatabase.queryDatabase("SELECT guild_id FROM guilds")]
    print("Logged in as {0.user}".format(whymightaGlobalVariables.bot))


@whymightaGlobalVariables.bot.event
async def on_message(message):
    channel = message.channel
    if message.author.bot is not True:
        if message.content == whymightaGlobalVariables.bot.command_prefix:
            await channel.send("Please check j!help for available functions")
        if whymightaGlobalVariables.bot.command_prefix + "reddit" in message.content:
            await RedditHandler(whymightaGlobalVariables.bot).on_reddit_message(message)
        elif whymightaGlobalVariables.bot.command_prefix + "apex" in message.content:
            await ApexHandler(whymightaGlobalVariables.bot).apex_message(message)


whymightaGlobalVariables.bot.run(TOKEN)
