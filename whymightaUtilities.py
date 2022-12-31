import disnake
import time
import whymightaGlobalVariables
@whymightaGlobalVariables.bot.slash_command(
    description="Check the latency of the whymighta",
    guild_ids=whymightaGlobalVariables.guild_ids)
async def ping(inter):
    before = time.monotonic()
    embed = disnake.Embed(title=":information_source: | Pong!", description="\n", color=0x9534eb)
    await inter.response.send_message(embed=embed)
    latency = (time.monotonic() - before) * 1000
    embed.add_field(name="Latency", value=str(int(latency)) + "ms", inline=False)
    embed.add_field(name="API", value=str(int(whymightaGlobalVariables.bot.latency * 1000)) + "ms", inline=False)
    await inter.edit_original_response(embed=embed)

# Only allow command if message author is an administrator to prevent trolling
@whymightaGlobalVariables.bot.slash_command(
    description="Clear up to 100 messages from the current channel at once",
    guild_ids=whymightaGlobalVariables.guild_ids)
async def clear(inter, number: int = 5):
    if number < 1 or number > 100:
        await inter.response.send_message("Error clearing messages from channel")
    else:
        await clearMessage(inter, number)
        await inter.channel.purge(limit=number)

async def clearMessage(inter, number):
    if number == 1:
        await inter.response.send_message(f"{inter.author} cleared {number} message from the channel")
    else:
        await inter.response.send_message(f"{inter.author} cleared {number} messages from the channel")
