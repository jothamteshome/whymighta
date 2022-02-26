import discord
import PropertiesReader
import pytz

from discord.ext import commands
from datetime import datetime, timezone

# Initialize reader for properties file
prop_reader = PropertiesReader.PropertiesReader()

# Load bot token from a file
TOKEN = prop_reader.get('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.guilds = True
intents.typing = True

# Instantiate a Discord client
bot = discord.ext.commands.Bot(command_prefix='j!', intents=intents)


@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))
    bot.load_extension("OhYa-Bot-OpenWeatherMap")
    bot.load_extension("OhYa-Bot-Reddit")
    bot.load_extension("OhYa-Bot-Help")
    bot.load_extension("OhYa-Bot-Clear")


@commands.command(name='ping')
async def ping(message):
    embed = discord.Embed(title="Pong!", color=0x9534eb)
    embed.add_field(name="Latency", value=str(round(bot.latency * 1000)) + "ms")
    await message.channel.send(embed=embed)


@bot.event
async def on_message(message):
    channel = message.channel
    if message.author.bot is not True:
        if message.content == bot.command_prefix:
            await channel.send("Did you mean to use a function?\n Current functions: weather")
        if bot.command_prefix + "help" in message.content:
            help_cog = bot.get_cog('HelpHandler')
            await help_cog.help(message)
        elif bot.command_prefix + "weather" in message.content:
            weather_cog = bot.get_cog('OpenWeatherHandler')
            await weather_cog.weather_message(message)
        elif bot.command_prefix + "reddit" in message.content:
            reddit_cog = bot.get_cog('RedditHandler')
            await reddit_cog.on_reddit_message(message)
        elif bot.command_prefix + "clear" in message.content:
            clear_cog = bot.get_cog('ClearHandler')
            await clear_cog.on_clear_message(message)
        elif bot.command_prefix + "ping" in message.content:
            await ping(message)


bot.run(TOKEN)
