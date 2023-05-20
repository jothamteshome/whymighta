import math
import disnake
import time

import whymightaDatabase
import whymightaGlobalVariables
import whymightaSupportFunctions


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


@whymightaGlobalVariables.bot.slash_command(
    description="Clear up to 100 messages from the current channel at once",
    guild_ids=whymightaGlobalVariables.guild_ids)
async def clear(inter, number: int = 5):
    if number < 1 or number > 100:
        await inter.response.send_message("Error clearing messages from channel")
    else:
        await whymightaSupportFunctions.clearMessage(inter, number)
        await inter.channel.purge(limit=number)


@whymightaGlobalVariables.bot.slash_command(
    description="Toggles the mock status of the bot",
    guild_ids=whymightaGlobalVariables.guild_ids)
async def toggle_mock(inter):
    if whymightaDatabase.toggleMock(inter.guild_id):
        await inter.response.send_message("Mocking has been enabled")
    else:
        await inter.response.send_message("Mocking has been disabled")


@whymightaGlobalVariables.bot.slash_command(
    description="Toggles the binary writing status of the bot",
    guild_ids=whymightaGlobalVariables.guild_ids)
async def toggle_binary(inter):
    if whymightaDatabase.toggleBinary(inter.guild_id):
        await inter.response.send_message("Binary has been enabled")
    else:
        await inter.response.send_message("Binary has been disabled")


@whymightaGlobalVariables.bot.slash_command(
    description="Checks the level of a user",
    guild_ids=whymightaGlobalVariables.guild_ids)
async def level(inter):
    curr_xp = whymightaDatabase.currentUserScore(inter.author.id, inter.guild_id)
    curr_level = whymightaSupportFunctions.check_level(curr_xp)

    curr_level_split = str(curr_level).split(".")

    next_level_progress = int(round(curr_level - int(curr_level_split[0]), 2) * 100)

    progress_bar = math.floor(next_level_progress / 10)

    embed = disnake.Embed(title=f"{inter.author.name}'s Level Progress", description="\n", color=0x9534eb)
    embed.add_field(name=f"{next_level_progress}% to Level {int(curr_level_split[0]) + 1}",
                    value=(progress_bar * "🔵") + ((10 - progress_bar) * "⚪"), inline=False)

    await inter.response.send_message(embed=embed)


@whymightaGlobalVariables.bot.slash_command(
    description="Puts a deserving criminal behind bars",
    guild_ids=whymightaGlobalVariables.guild_ids)
async def jail(inter, name):
    members = {member.name: member for member in inter.guild.members}
    nicknames = {member.nick: member for member in inter.guild.members}

    if name in members:
        await inter.response.send_message("Generating Image...")
        jailed_image = whymightaSupportFunctions.imprisonMember(members[name])
        await inter.edit_original_response(content="", file=jailed_image)
    elif name in nicknames:
        await inter.response.send_message("Generating Image...")
        jailed_image = whymightaSupportFunctions.imprisonMember(nicknames[name])
        await inter.edit_original_response(content="", file=jailed_image)
    else:
        await inter.response.send_message("User does not exist. Please try again with the user's discord name")
