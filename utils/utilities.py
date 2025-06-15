import disnake
import io
import math
import requests
import random
import utils.database as database
import whymightaGlobalVariables
import hashlib

from PIL import Image


# Mocks a user's message by responding to it in "spongebob" case
# after filtering out links and attachments
async def mock_user(message):
    channel = message.channel
    if await database.query_mock(message.guild.id):
        if "http" in message.content.split("://")[0]:
            await channel.send(message.content)
        elif len(message.attachments) > 0:
            if message.content != "":
                await channel.send(sPoNgEbObCaSe(message.content))
            for attachment in message.attachments:
                await channel.send(attachment)
        else:
            await channel.send(sPoNgEbObCaSe(message.content))


async def binarize_message(message):
    channel = message.channel
    if await database.query_binary(message.guild.id):
        if "http" in message.content.split("://")[0]:
            await channel.send(message.content)
        elif len(message.attachments) > 0:
            if message.content != "":
                await channel.send(binarizeMessage(message.content))
            for attachment in message.attachments:
                await channel.send(attachment)
        else:
            await channel.send(binarizeMessage(message.content))


def binarizeMessage(message):
    return ' '.join(format(ord(char), '08b') for char in message)


# Rewrites message in "Spongebob" case
def sPoNgEbObCaSe(message):
    mocking_message = ""

    uppercase = False

    for char in message:
        if uppercase:
            mocking_message += char.upper()
            uppercase = False

        else:
            mocking_message += char.lower()
            uppercase = True

    return mocking_message


# Give user xp based on message contents
async def give_user_message_xp(message, catchingUp):
    mentions_xp = len(message.mentions) * 5
    attachments_xp = len(message.attachments) * 10
    content_xp = len(message.content)

    prev_xp = await database.current_user_score(message.author.id, message.guild.id)
    curr_xp = prev_xp + mentions_xp + attachments_xp + content_xp

    if not catchingUp:
        await announce_level_up(prev_xp, curr_xp, message.author, message.channel)

    await database.update_user_score(message.author.id, message.guild.id, curr_xp)
    await database.update_last_message_sent(message.guild.id, message.created_at)


async def give_user_inter_xp(inter, catchingUp):
    if inter.data.name != "level":
        score = 5
        for option in inter.options:
            score += len(option)

        prev_xp = await database.current_user_score(inter.author.id, inter.guild_id)
        curr_xp = prev_xp + score

        if not catchingUp:
            await announce_level_up(prev_xp, curr_xp, inter.author, inter.channel)

        await database.update_user_score(inter.author.id, inter.guild_id, curr_xp)
        await database.update_last_message_sent(inter.guild.id, inter.created_at)


# Announce if a user has leveled up
async def announce_level_up(previous_xp, current_xp, user, text_channel):
    prev_level = check_level(previous_xp)
    curr_level = check_level(current_xp)

    if math.floor(curr_level) > math.floor(prev_level):
        bot_channel_id = await database.get_bot_text_channel_id(text_channel.guild.id)

        if not bot_channel_id:
            await text_channel.send(f"Congratulations {user.mention}! You've reached Level {math.floor(curr_level)}!")
        else:
            bot_channel = whymightaGlobalVariables.bot.get_channel(bot_channel_id)

            await bot_channel.send(f"Congratulations {user.mention}! You've reached Level {math.floor(curr_level)}!")


# Checks the level of a user based on their exp accrued
def check_level(current_score):
    level = current_score ** (1/5)

    return level


# Sends message informing number of messages cleared from channel
async def clearMessage(inter, number):
    if number == 1:
        await inter.response.send_message(f"{inter.author} cleared {number} message from the channel")
    else:
        await inter.response.send_message(f"{inter.author} cleared {number} messages from the channel")


# Takes in a server member and returns an image with them behind bars
def imprisonMember(member):
    # Max size for image
    MAX_IMG_SIZE = 1024

    # Get member avatar from Discord
    avatar_url = member.display_avatar.url
    response = requests.get(avatar_url)
    avatar = Image.open(io.BytesIO(response.content))
    avatar = avatar.convert("RGBA")

    # Load Prison Bar image
    prison_bars = Image.open("Images/prison_bars.png")

    # Calculate proper cropping of prison bar image
    prison_bar_mid = int(prison_bars.width / 2)
    left = prison_bar_mid - int(MAX_IMG_SIZE / 2)
    right = prison_bar_mid + int(MAX_IMG_SIZE / 2)
    prison_bars = prison_bars.crop((left, 0, right, MAX_IMG_SIZE))

    # Calculate proper resizing of prison bar image
    width_ratio = avatar.width / prison_bars.width
    height = int(prison_bars.height * width_ratio)
    prison_bars = prison_bars.resize((avatar.width, height))

    # Overlay prison bars over avatar
    imprisoned_avatar = Image.alpha_composite(avatar, prison_bars)
    imprisoned_avatar = Image.alpha_composite(imprisoned_avatar, prison_bars)

    # Create a disnake file object using the image and return for sending
    with io.BytesIO() as image_binary:
        imprisoned_avatar.save(image_binary, 'PNG')
        image_binary.seek(0)

        return disnake.File(fp=image_binary, filename='image.png')


async def serverMessageCatchUp(bot):
    # Loop through all guilds the bot is a part of
    for guild in bot.guilds:

        # Retrieve the time of the last message the bot saw
        last_server_message_time = await database.query_last_message_sent(guild.id)

        # Initialize the latest message time
        latest_message_time = last_server_message_time

        # Loop through all text channels in guild
        for channel in guild.channels:
            if type(channel) == disnake.TextChannel:
                # Load messages sent after last seen message
                new_messages = await channel.history(after=last_server_message_time, oldest_first=True).flatten()

                # Give user xp for messages sent since bot was last online
                for message in new_messages:
                    if message.interaction_metadata is None:
                        if not message.author.bot:
                            await give_user_message_xp(message, catchingUp=True)

                # Store the latest message sent in the channel
                latest_channel_message = new_messages.pop() if len(new_messages) > 0 else None

                # Save the current channel's latest message time if it is
                # more recent than the previous most recent message
                if latest_channel_message is not None and latest_message_time < latest_channel_message.created_at:
                    latest_message_time = latest_channel_message.created_at

        # Update guild's latest message time to be the most recent of all messages in guild
        await database.update_last_message_sent(guild.id, latest_message_time)


async def updateNewMembers(bot):
    # Loop through all guilds bot is a part of
    for guild in bot.guilds:
        # Add all users that joined while the bot was offline
        member_ids = [member.id for member in guild.members if not member.bot]

        await database.add_guild(guild.id, defaultGuildTextChannel(guild))
        await database.add_users(member_ids, guild.id)


# Replaces the tokens in a chatbot reply
def replaceTokens(token, tokenCount, tokenGuildList, author, reply):
    if tokenCount < 2:
        tokenReplaceList = [author.mention]
    else:
        tokenReplaceList = [author.mention]
        token_replace_weights = [1 if member is not author else 2 for member in tokenGuildList]
        selected_mentions = random.choices(tokenGuildList, token_replace_weights, k=tokenCount - 1)
        tokenReplaceList.extend(selected_mentions)

    for i in range(tokenCount):
        reply = reply.replace(token, tokenReplaceList[i], 1)

    return reply


def checkAdmin(author):
    return author.top_role.permissions.administrator or author.guild.owner == author


def defaultGuildTextChannel(guild):
    default_text_channel = None

    if guild.text_channels:
        default_text_channel = guild.text_channels[0].id

    return default_text_channel


def md5_hash(unhashed_string):
    return hashlib.md5(unhashed_string.encode('utf-8')).hexdigest()


async def delete_thread(guild, thread_id):
    # Get thread by id
    thread = guild.get_thread(thread_id)

    # Delete thread
    await thread.delete()

    # Remove thread from database
    await database.remove_thread_id(thread_id)

    return thread.name
