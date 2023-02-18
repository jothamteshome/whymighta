import disnake
import whymightaDatabase
import whymightaGlobalVariables
import whymightaSupportFunctions
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
    if message.author.bot is not True:
        await whymightaSupportFunctions.give_user_xp(message.guild.id, message.author.id, message)
        await whymightaSupportFunctions.mock_user(message)


@whymightaGlobalVariables.bot.event
async def on_guild_join(guild):
    member_ids = [member.id for member in guild.members if not member.bot]
    whymightaDatabase.addGuild(guild.id)
    whymightaDatabase.addUsers(member_ids, guild.id)


@whymightaGlobalVariables.bot.event
async def on_guild_remove(guild):
    whymightaDatabase.removeGuild(guild.id)


@whymightaGlobalVariables.bot.event
async def on_application_command(inter):
    if inter.data.name != "level":
        score = 5
        for option in inter.options:
            score += len(option)

        prev_xp = whymightaDatabase.currentUserScore(inter.author.id, inter.guild_id)
        curr_xp = prev_xp + score

        await whymightaSupportFunctions.announce_level_up(prev_xp, curr_xp, inter.author, inter.channel)

        whymightaDatabase.updateUserScore(inter.author.id, inter.guild_id, curr_xp)
    await whymightaGlobalVariables.bot.process_application_commands(inter)


@whymightaGlobalVariables.bot.event
async def on_member_join(member):
    whymightaDatabase.addUser(member.id, member.guild.id)


@whymightaGlobalVariables.bot.event
async def on_member_remove(member):
    whymightaDatabase.removeUser(member.id, member.guild.id)


whymightaGlobalVariables.bot.run(TOKEN)
