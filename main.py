import os
import disnake
from core.config import config
from disnake.ext import commands
from utils.database import Database
from utils.helpers import Helpers

# Retrieve bot token from database
TOKEN = config.DISCORD_TOKEN

# Instantiate a Discord client
bot = commands.InteractionBot(intents=disnake.Intents.all())
database = Database()
helpers = Helpers(bot)


@bot.event
async def on_ready():
    await database.create_tables()
    await helpers.update_new_members()
    await helpers.server_message_catchup()
    print(f"Logged in as {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot is not True:
        if bot.user in message.mentions:
            cog = bot.get_cog("Chatbot")
            if cog:
                await cog.chatting(message)
        await helpers.give_user_message_xp(message, catchingUp=False)
        await helpers.mock_user(message)
        await helpers.binarize_message(message)


@bot.event
async def on_guild_join(guild):
    member_ids = [member.id for member in guild.members if not member.bot]
    
    await database.add_guild(guild.id, helpers.default_guild_text_channel(guild))
    await database.add_users(member_ids, guild.id)


@bot.event
async def on_guild_remove(guild):
    await database.remove_guild(guild.id)


@bot.event
async def on_application_command(inter):
    await bot.process_application_commands(inter)
    await helpers.give_user_inter_xp(inter, catchingUp=False)


@bot.event
async def on_member_join(member):
    await database.add_user(member.id, member.guild.id)


@bot.event
async def on_member_remove(member):
    await database.removeUser(member.id, member.guild.id)


@bot.event
async def on_guild_channel_delete(channel):
    bot_text_channel_id = await database.get_bot_text_channel_id(channel.guild.id)

    if channel.id == bot_text_channel_id:
        await database.set_bot_text_channel_id(helpers.default_guild_text_channel(channel.guild))


# Load cogs from the 'cogs' directory
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        name, ext = os.path.splitext(filename)

        # Only load cog_manager in debug mode
        if name == "cog_manager" and not config.DEBUG:
            continue

        bot.load_extension(f"cogs.{name}")

bot.run(TOKEN)