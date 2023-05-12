import whymightaDatabase
import math


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
