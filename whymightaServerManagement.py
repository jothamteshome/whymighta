import disnake
import json
import random

import whymightaGlobalVariables
import whymightaDatabase
import whymightaSupportFunctions

from io import BytesIO


@whymightaGlobalVariables.bot.slash_command(
        default_member_permissions=disnake.Permissions(administrator=True)
)
async def manage(inter):
    pass

@manage.sub_command_group()
async def bot_channel(inter):
    pass

@bot_channel.sub_command(
        description="Set a new channel as the default bot channel"
)
async def set(inter):
    await inter.response.defer()    

    whymightaDatabase.setBotTextChannelID(inter.guild.id, inter.channel.id)

    await inter.edit_original_message(f"Bot messages will now appear in {inter.channel.name}!")


@bot_channel.sub_command(
        description="Get name of current bot channel"
)
async def get(inter):
    await inter.response.defer()
    

    bot_channel_id = whymightaDatabase.getBotTextChannelID(inter.guild.id)
    bot_channel = None


    for channel in inter.guild.text_channels:
        if channel.id == bot_channel_id:
            bot_channel = channel.name
            break
    
    
    if bot_channel is not None:
        await inter.edit_original_message(f"Current bot text channel is #{bot_channel}")
    else:
        await inter.edit_original_message(f"No channel has been set as the bot channel")


@manage.sub_command(
    description="Clear up to 100 messages from the current channel at once")
async def clear(inter, number: int = 5):
    if number < 1 or number > 100:
        await inter.response.send_message("Error clearing messages from channel")
    else:
        await whymightaSupportFunctions.clearMessage(inter, number)
        await inter.channel.purge(limit=number+1)


@manage.sub_command_group()
async def toggle(inter):
    pass


@toggle.sub_command(description="Toggles the mock status of the bot")
async def mock(inter):
    await inter.response.defer()

    if whymightaDatabase.toggleMock(inter.guild_id):
        await inter.edit_original_message("Mocking has been enabled")
    else:
        await inter.edit_original_message("Mocking has been disabled")


@toggle.sub_command(description="Toggles the binary writing status of the bot")
async def binary(inter):
    await inter.response.defer()

    if whymightaDatabase.toggleBinary(inter.guild_id):
        await inter.edit_original_message("Binary has been enabled")
    else:
        await inter.edit_original_message("Binary has been disabled")


@manage.sub_command_group()
async def theme(inter):
    pass


@theme.sub_command(
    description="Randomly updates server nicknames based on those found in uploaded file"
)
async def set(inter, file: disnake.Attachment):
    await inter.response.defer()

    # Check that file is a json file
    if 'application/json' not in file.content_type:
        await inter.edit_original_message("File must be a json")
        return
    
    # Store file in memory and open it
    fp = BytesIO()
    await file.save(fp)
    server_structure = json.load(fp)

    # Check that required names field exists in JSON file
    if "names" not in server_structure:
        await inter.edit_original_message("Please make sure `names` key exists in JSON")
        return
    elif "names" in server_structure and "list" not in str(type(server_structure['names'])):
        await inter.edit_original_message("Please make sure the value of `names` is a list")
        return

    
    if len(server_structure["names"]) < len(inter.guild.members):
        await inter.edit_original_message(f"Please provide enough names to allocate one for each member in server ({len(inter.guild.members) - len(server_structure['names'])} more required)")
        return
    

    # Shuffle list of names
    new_nicks = server_structure['names']
    random.shuffle(new_nicks)

    # Assign new names to each user
    for member in inter.guild.members:
        new_nick = new_nicks.pop()

        # If bot does not have permission to assign a name, send the names as a message
        try:
            await member.edit(nick=new_nick)
        except disnake.errors.Forbidden:
            await inter.channel.send(f"{member.name} - {new_nick}")
            continue


    await inter.edit_original_message("Random nicknames have been assigned")