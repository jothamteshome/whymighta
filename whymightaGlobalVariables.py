import disnake
import PropertiesReader

prop_reader = PropertiesReader.PropertiesReader()

from disnake.ext import commands

guild_ids = []
intents = disnake.Intents.all()


# Instantiate a Discord client
bot = disnake.ext.commands.InteractionBot(intents=intents)

file = prop_reader.open("GUILD_IDS", "r")
for guild_id in file:
    guild_id = guild_id.replace("\n", "")
    guild_ids.append(int(guild_id))
file.close()

