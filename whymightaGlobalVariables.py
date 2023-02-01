import disnake

from disnake.ext import commands

guild_ids = []

intents = disnake.Intents.all()

# Instantiate a Discord client
bot = disnake.ext.commands.InteractionBot(intents=intents)
