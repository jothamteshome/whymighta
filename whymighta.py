import disnake

import whymightaDatabase
import whymightaGlobalVariables
import utils.utilities as utilities
import whymightaServerManagement
import whymightaUtilities
import whymightaHelp
import whymightaOpenWeatherMap
import whymightaFortnite
import whymightaGames
import whymightaChatbot

from core.config import config

# Retrieve bot token from database
TOKEN = config.DISCORD_TOKEN


@whymightaGlobalVariables.bot.event
async def on_ready():
    await whymightaDatabase.create_tables()
    await utilities.updateNewMembers(whymightaGlobalVariables.bot)
    await utilities.serverMessageCatchUp(whymightaGlobalVariables.bot)
    print("Logged in as {0.user}".format(whymightaGlobalVariables.bot))


@whymightaGlobalVariables.bot.event
async def on_message(message):
    if message.author.bot is not True:
        if whymightaGlobalVariables.bot.user in message.mentions:
            await whymightaChatbot.chatting(message)
        await utilities.give_user_message_xp(message, catchingUp=False)
        await utilities.mock_user(message)
        await utilities.binarize_message(message)


@whymightaGlobalVariables.bot.event
async def on_guild_join(guild):
    member_ids = [member.id for member in guild.members if not member.bot]
    
    await whymightaDatabase.add_guild(guild.id, utilities.defaultGuildTextChannel(guild))
    await whymightaDatabase.add_users(member_ids, guild.id)


@whymightaGlobalVariables.bot.event
async def on_guild_remove(guild):
    await whymightaDatabase.remove_guild(guild.id)


@whymightaGlobalVariables.bot.event
async def on_application_command(inter):
    await whymightaGlobalVariables.bot.process_application_commands(inter)
    await utilities.give_user_inter_xp(inter, catchingUp=False)


@whymightaGlobalVariables.bot.event
async def on_member_join(member):
    await whymightaDatabase.add_user(member.id, member.guild.id)


@whymightaGlobalVariables.bot.event
async def on_member_remove(member):
    await whymightaDatabase.removeUser(member.id, member.guild.id)


@whymightaGlobalVariables.bot.event
async def on_guild_channel_delete(channel):
    bot_text_channel_id = await whymightaDatabase.get_bot_text_channel_id(channel.guild.id)

    if channel.id == bot_text_channel_id:
        await whymightaDatabase.set_bot_text_channel_id(utilities.defaultGuildTextChannel(channel.guild))

whymightaGlobalVariables.bot.run(TOKEN)
