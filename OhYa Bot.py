import discord
import PropertiesReader

from discord.ext import commands

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


@bot.event
async def on_message(message):
    channel = message.channel
    if message.author.bot is not True:
        if message.content == bot.command_prefix:
            await channel.send("Did you mean to use a function?\n Current functions: weather")
        if bot.command_prefix + "help" in message.content:
            await channel.send("*Weather :* j!weather [City-Name] [State-Code*(optional)*] "
                               "[Country-Code*(optional)*] [Units-Type]")
        elif bot.command_prefix + "weather" in message.content:
            bot.load_extension("OhYa-Bot-OpenWeatherMap")
            weather_cog = bot.get_cog('OpenWeatherHandler')
            await weather_cog.weather_message(message)
        elif bot.command_prefix + "reddit" in message.content:
            bot.load_extension("OhYa-Bot-Reddit")
            reddit_cog = bot.get_cog('RedditHandler')
            await reddit_cog.on_reddit_message(message)


bot.run(TOKEN)
