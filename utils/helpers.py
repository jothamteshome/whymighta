import disnake
import io
import math
import requests

from PIL import Image
from utils.database import Database

class Helpers:
    def __init__(self, bot):
        self.bot = bot
        self.database = Database()


    # Mocks a user's message by responding to it in "spongebob" case
    # after filtering out links and attachments
    async def mock_user(self, message):
        channel = message.channel
        if await self.database.query_mock(message.guild.id):
            if "http" in message.content.split("://")[0]:
                await channel.send(message.content)
            elif len(message.attachments) > 0:
                if message.content != "":
                    await channel.send(self.spongebob_case(message.content))
                for attachment in message.attachments:
                    await channel.send(attachment)
            else:
                await channel.send(self.spongebob_case(message.content))


    async def binarize_message(self, message):
        channel = message.channel
        if await self.database.query_binary(message.guild.id):
            if "http" in message.content.split("://")[0]:
                await channel.send(message.content)
            elif len(message.attachments) > 0:
                if message.content != "":
                    await channel.send(self.convert_binary(message.content))
                for attachment in message.attachments:
                    await channel.send(attachment)
            else:
                await channel.send(self.convert_binary(message.content))


    def convert_binary(self, message):
        return ' '.join(format(ord(char), '08b') for char in message)


    # Rewrites message in "Spongebob" case
    def spongebob_case(self, message):
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
    async def give_user_message_xp(self, message, catchingUp):
        mentions_xp = len(message.mentions) * 5
        attachments_xp = len(message.attachments) * 10
        content_xp = len(message.content)

        prev_xp = await self.database.current_user_score(message.author.id, message.guild.id)
        curr_xp = prev_xp + mentions_xp + attachments_xp + content_xp

        if not catchingUp:
            await self.announce_level_up(prev_xp, curr_xp, message.author, message.channel)

        await self.database.update_user_score(message.author.id, message.guild.id, curr_xp)
        await self.database.update_last_message_sent(message.guild.id, message.created_at)


    async def give_user_inter_xp(self, inter, catchingUp):
        if inter.data.name != "level":
            score = 5
            for option in inter.options:
                score += len(option)

            prev_xp = await self.database.current_user_score(inter.author.id, inter.guild_id)
            curr_xp = prev_xp + score

            if not catchingUp:
                await self.announce_level_up(prev_xp, curr_xp, inter.author, inter.channel)

            await self.database.update_user_score(inter.author.id, inter.guild_id, curr_xp)
            await self.database.update_last_message_sent(inter.guild.id, inter.created_at)


    # Announce if a user has leveled up
    async def announce_level_up(self, previous_xp, current_xp, user, text_channel):
        prev_level = self.check_level(previous_xp)
        curr_level = self.check_level(current_xp)

        if math.floor(curr_level) > math.floor(prev_level):
            bot_channel_id = await self.database.get_bot_text_channel_id(text_channel.guild.id)

            if not bot_channel_id:
                await text_channel.send(f"Congratulations {user.mention}! You've reached Level {math.floor(curr_level)}!")
            else:
                bot_channel = self.bot.get_channel(bot_channel_id)

                await bot_channel.send(f"Congratulations {user.mention}! You've reached Level {math.floor(curr_level)}!")


    # Checks the level of a user based on their exp accrued
    def check_level(self, current_score):
        level = current_score ** (1/5)

        return level            


    # Takes in a server member and returns an image with them behind bars
    def imprison_member(self, member):
        # Max size for image
        MAX_IMG_SIZE = 1024

        # Get member avatar from Discord
        avatar_url = member.display_avatar.url
        response = requests.get(avatar_url)
        avatar = Image.open(io.BytesIO(response.content))
        avatar = avatar.convert("RGBA")

        # Load Prison Bar image
        prison_bars = Image.open("images/prison_bars.png")

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


    async def server_message_catchup(self):
        # Loop through all guilds the bot is a part of
        for guild in self.bot.guilds:

            # Retrieve the time of the last message the bot saw
            last_server_message_time = await self.database.query_last_message_sent(guild.id)

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
                                await self.give_user_message_xp(message, catchingUp=True)

                    # Store the latest message sent in the channel
                    latest_channel_message = new_messages.pop() if len(new_messages) > 0 else None

                    # Save the current channel's latest message time if it is
                    # more recent than the previous most recent message
                    if latest_channel_message is not None and latest_message_time < latest_channel_message.created_at:
                        latest_message_time = latest_channel_message.created_at

            # Update guild's latest message time to be the most recent of all messages in guild
            await self.database.update_last_message_sent(guild.id, latest_message_time)


    async def update_new_members(self):
        # Loop through all guilds bot is a part of
        for guild in self.bot.guilds:
            # Add all users that joined while the bot was offline
            member_ids = [member.id for member in guild.members if not member.bot]

            await self.database.add_guild(guild.id, self.default_guild_text_channel(guild))
            await self.database.add_users(member_ids, guild.id)


    def default_guild_text_channel(self, guild):
        default_text_channel = None

        if guild.text_channels:
            default_text_channel = guild.text_channels[0].id

        return default_text_channel


    async def delete_thread(self, guild, thread_id):
        # Get thread by id
        thread = guild.get_thread(thread_id)

        # Delete thread
        await thread.delete()

        # Remove thread from database
        await self.database.remove_thread_id(thread_id)

        return thread.name
