import whymightaDatabase
import math
import io
import disnake
import requests

from PIL import Image


# Mocks a user's message by responding to it in "spongebob" case
# after filtering out links and attachments
async def mock_user(message):
    channel = message.channel
    if whymightaDatabase.queryMock(message.guild.id):
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
    if whymightaDatabase.queryBinary(message.guild.id):
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
async def give_user_xp(guild_id, user_id, message):
    mentions_xp = len(message.mentions) * 5
    attachments_xp = len(message.attachments) * 10
    content_xp = len(message.content)

    prev_xp = whymightaDatabase.currentUserScore(user_id, guild_id)
    curr_xp = prev_xp + mentions_xp + attachments_xp + content_xp

    await announce_level_up(prev_xp, curr_xp, message.author, message.channel)

    whymightaDatabase.updateUserScore(user_id, guild_id, curr_xp)


# Announce if a user has leveled up
async def announce_level_up(previous_xp, current_xp, user, text_channel):
    prev_level = check_level(previous_xp)
    curr_level = check_level(current_xp)

    if math.floor(curr_level) > math.floor(prev_level):
        await text_channel.send(f"Congratulations {user.mention}! You've reached Level {math.floor(curr_level)}!")


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
