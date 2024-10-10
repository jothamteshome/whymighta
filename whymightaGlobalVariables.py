import disnake

from disnake.ext import commands

intents = disnake.Intents.all()

# Instantiate a Discord client
bot = disnake.ext.commands.InteractionBot(intents=intents)
