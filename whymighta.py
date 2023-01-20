import disnake
import whymightaGlobalVariables
import whymightaUtilities
import whymightaHelp
import whymightaOpenWeatherMap
import whymightaBirthdays

from whymightaApex import ApexHandler
from whymightaReddit import RedditHandler
from whymightaTheList import TheListHandler



# Load bot token from a file
TOKEN = whymightaGlobalVariables.prop_reader.get_key('DISCORD_TOKEN')

@whymightaGlobalVariables.bot.event
async def on_ready():
    whymightaBirthdays.loadBirthdays()
    whymightaBirthdays.birthdayCheck.start()
    whymightaBirthdays.saveBirthdays.start()
    print("Logged in as {0.user}".format(whymightaGlobalVariables.bot))


@whymightaGlobalVariables.bot.event
async def on_message(message):
    channel = message.channel
    if message.author.bot is not True:
        if message.content == whymightaGlobalVariables.bot.command_prefix:
            await channel.send("Please check j!help for available functions")
        if whymightaGlobalVariables.bot.command_prefix + "reddit" in message.content:
            await RedditHandler(whymightaGlobalVariables.bot).on_reddit_message(message)
        elif whymightaGlobalVariables.bot.command_prefix + "the_list" in message.content:
            await TheListHandler(whymightaGlobalVariables.bot).on_list_message(message)
        elif whymightaGlobalVariables.bot.command_prefix + "apex" in message.content:
            await ApexHandler(whymightaGlobalVariables.bot).apex_message(message)


whymightaGlobalVariables.bot.run(TOKEN)
