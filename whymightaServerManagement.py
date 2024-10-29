import whymightaGlobalVariables
import whymightaDatabase
import whymightaSupportFunctions


@whymightaGlobalVariables.bot.slash_command(
        description="Set a new channel as the default bot channel"
)
async def set_bot_channel(inter):
    await inter.response.defer()

    if not whymightaSupportFunctions.checkAdmin(inter.author):
        await inter.edit_original_message("Only users with Administrator priviledges may use this function")
        return
    

    whymightaDatabase.setBotTextChannel(inter.guild.id, inter.channel.id)

    await inter.edit_original_message(f"Bot messages will now appear in {inter.channel.name}!")



@whymightaGlobalVariables.bot.slash_command(
        description="Get name of current bot channel"
)
async def get_bot_channel(inter):
    await inter.response.defer()

    if not whymightaSupportFunctions.checkAdmin(inter.author):
        await inter.edit_original_message("Only users with Administrator priviledges may use this function")
        return
    

    bot_channel_id = whymightaDatabase.getBotTextChannel(inter.guild.id)
    bot_channel = None


    for channel in inter.guild.text_channels:
        if channel.id == bot_channel_id:
            bot_channel = channel.name
            break
    
    
    if bot_channel is not None:
        await inter.edit_original_message(f"Current bot text channel is #{bot_channel}")
    else:
        await inter.edit_original_message(f"No channel has been set as the bot channel")