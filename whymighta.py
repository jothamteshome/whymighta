import disnake

import whymightaDatabase
import whymightaGlobalVariables
import whymightaSupportFunctions
import whymightaServerManagement
import whymightaUtilities
import whymightaHelp
import whymightaOpenWeatherMap
import whymightaBirthdays
import whymightaFortnite

# Retrieve bot token from database
TOKEN = whymightaDatabase.getKey('DISCORD_TOKEN')


@whymightaGlobalVariables.bot.event
async def on_ready():
    whymightaBirthdays.birthdayCheck.start()

    await whymightaSupportFunctions.updateNewMembers(whymightaGlobalVariables.bot)
    await whymightaSupportFunctions.serverMessageCatchUp(whymightaGlobalVariables.bot)
    print("Logged in as {0.user}".format(whymightaGlobalVariables.bot))


@whymightaGlobalVariables.bot.event
async def on_message(message):
    if message.author.bot is not True:
        await whymightaSupportFunctions.give_user_message_xp(message, catchingUp=False)
        await whymightaSupportFunctions.mock_user(message)
        await whymightaSupportFunctions.binarize_message(message)


@whymightaGlobalVariables.bot.event
async def on_guild_join(guild):
    member_ids = [member.id for member in guild.members if not member.bot]
    
    whymightaDatabase.addGuild(guild.id, whymightaSupportFunctions.defaultGuildTextChannel(guild))
    whymightaDatabase.addUsers(member_ids, guild.id)


@whymightaGlobalVariables.bot.event
async def on_guild_remove(guild):
    whymightaDatabase.removeGuild(guild.id)


@whymightaGlobalVariables.bot.event
async def on_application_command(inter):
    await whymightaSupportFunctions.give_user_inter_xp(inter, catchingUp=False)
    await whymightaGlobalVariables.bot.process_application_commands(inter)


@whymightaGlobalVariables.bot.event
async def on_member_join(member):
    whymightaDatabase.addUser(member.id, member.guild.id)


@whymightaGlobalVariables.bot.event
async def on_member_remove(member):
    whymightaDatabase.removeUser(member.id, member.guild.id)


@whymightaGlobalVariables.bot.event
async def on_guild_channel_delete(channel):
    bot_text_channel = whymightaDatabase.getBotTextChannel(channel.guild.id)

    if channel.id == bot_text_channel:
        whymightaDatabase.setBotTextChannel(whymightaSupportFunctions.defaultGuildTextChannel(channel.guild))

whymightaGlobalVariables.bot.run(TOKEN)
