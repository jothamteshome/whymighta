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
        if whymightaDatabase.queryMock(message.guild.id):
            if "http" in message.content.split("://")[0]:
                await channel.send(message.content)
            elif len(message.attachments) > 0:
                if message.content != "":
                    await channel.send(whymightaUtilities.sPoNgEbObCaSe(message.content))
                for attachment in message.attachments:
                    await channel.send(attachment)
            else:
                await channel.send(whymightaUtilities.sPoNgEbObCaSe(message.content))


whymightaGlobalVariables.bot.run(TOKEN)
