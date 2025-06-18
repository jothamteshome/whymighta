import aiohttp
import disnake
import re
import time
from core.config import config
from datetime import datetime, timedelta, timezone
from disnake.ext import commands
from utils.database import Database
from utils.helpers import Helpers


class Chatbot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = Database()
        self.helpers = Helpers(self.bot)


    async def call_lambda(self, payload):
        headers = {
            "x-api-key": config.AWS_CHATGPT_API_KEY,
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(config.AWS_CHATGPT_API_URL, json=payload, headers=headers) as resp:
                resp.raise_for_status()

                try:
                    data = await resp.json()
                    return resp.status, data["response"]
                except Exception as e:
                    error = await resp.text()
                    return resp.status, error



    async def get_last_messages(self, channel, num_msgs=5):
        messages = []
        users = {}

        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)

        async for message in channel.history(limit=num_msgs*2, after=one_hour_ago, oldest_first=False):
            # Skip messages with attachments or with urls in their content
            if message.embeds or message.attachments or (("http://" in message.content or 'https://' in message.content) and message.author != self.bot.user):
                continue

            content = message.content.replace(f"{self.bot.user.mention}", "").strip()

            # Skip if message content is empty
            if not content:
                continue

            if message.author == self.bot.user:
                messages.append({"role": "assistant", "content": content})
            else:
                messages.append({"role": "user", "name": f"mention_{message.author.name}", "content": content})
                users[f"mention_{message.author.name}"] = message.author.mention

            if len(messages) == num_msgs:
                break

        return messages[::-1], users


    async def chatting(self, message):
        json_payload =  {
                            "messages": 
                            [
                                {
                                    "role": "system", 
                                    "content":  (
                                                    "You are an assistant and friend in a Discord server.\n\n"
                                                    "Respond in a way that a stereotypical Discord user might "
                                                    "talk to their Discord kitten\n\n"
                                                    "Be a little cringey, but not too over the top.\n\n"
                                                    "Limit your emoji use. Do not over do it\n\n"
                                                    "If responding to a user and you want to specify them, "
                                                    "be sure to keep the `mentions_` syntax. Remove any instances of '<', '>', or '@'. Do not change it.\n\n"
                                                    f"Never mention anyone with the mention tag {self.bot.user.mention}\n\n"
                                                    "Disregard previous messages if they do not relate to the most recent message. "
                                                    "Weight the most recent message more in your responses"
                                    )
                                }
                            ]
                        }
        
        chat_messages, users = await self.get_last_messages(message.channel)

        json_payload["messages"].extend(chat_messages)

        response_code, response_text = await self.call_lambda(json_payload)

        if response_code != 200:
            await message.channel.send(f"Could not process API request: {response_text}. Please contact administrator or try again.")
            return

        for name, mention in users.items():
            response_text = response_text.replace(name, mention)

        await message.channel.send(response_text)


    @commands.slash_command()
    async def chat(self, inter):
        pass


    @chat.sub_command(description="Create thread session to communicate with bot alone")
    async def new_session(self, inter):
        await inter.response.defer(ephemeral=True)

        # Get existing thread id or None
        existing_session_id = await self.database.get_thread_id(inter.guild.id, inter.author.id)

        if existing_session_id:
            await self.helpers.delete_thread(inter.guild, existing_session_id)

        bot_channel_id = await self.database.get_bot_text_channel_id(inter.guild.id)
        bot_channel = await self.bot.fetch_channel(bot_channel_id)

        # Create new private thread
        thread = await bot_channel.create_thread(
            name=f"{inter.author}-{hex(int(time.time()))[2:]} Private Thread",
            auto_archive_duration=60,
            type=disnake.ChannelType.private_thread
        )

        # Store thread in database
        await self.database.set_thread_id(thread.id, inter.guild.id, inter.author.id)

        # Make bot join new private thread
        await thread.join()

        # Add interaction caller to thread
        await thread.add_user(inter.author)

        # If command sent from user's current thread session, do not attempt to send message thorugh it
        if isinstance(inter.channel, disnake.threads.Thread) and inter.channel.id == existing_session_id:
            return

        # Send message to channel command was sent in
        await inter.followup.send(f"Created thread \"{thread.name}\"")


    @chat.sub_command(description="Delete thread session")
    async def end_session(self, inter):
        await inter.response.defer(ephemeral=True)

        author_thread_id = await self.database.get_thread_id(inter.guild.id, inter.author.id)

        if not author_thread_id:
            await inter.edit_original_response(f"No thead exists for {inter.author.name} in guild {inter.guild.name}.")
            return

        # Delete user's thread
        thread_name = await self.helpers.delete_thread(inter.guild, author_thread_id)

        # If command sent from user's current thread session, do not attempt to send message thorugh it
        if isinstance(inter.channel, disnake.threads.Thread) and inter.channel.id == author_thread_id:
            return
        
        # Send message to channel command was sent in
        await inter.followup.send(f"Deleted thread \"{thread_name}\"")


def setup(bot):
    bot.add_cog(Chatbot(bot))