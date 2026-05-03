import disnake
import logging
import time
from datetime import datetime, timedelta, timezone
from disnake.ext import commands

from database.manager import Database
from llm.client import get_llm_client
from llm.prompts import build_system_prompt
from models.theme import GuildTheme

HISTORY_TARGET = 5
HISTORY_FETCH_MULTIPLIER = 2

logger = logging.getLogger(__name__)


class Chatbot(commands.Cog):
    def __init__(self, bot: commands.InteractionBot) -> None:
        self.bot: commands.InteractionBot = bot
        self.database: Database = bot.db
        self.llm_client = get_llm_client()



    async def get_last_messages(
        self, channel: disnake.TextChannel, num_msgs: int = HISTORY_TARGET
    ) -> tuple[list[dict], dict[str, str]]:
        messages = []
        users = {}

        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)

        async for message in channel.history(limit=HISTORY_TARGET * HISTORY_FETCH_MULTIPLIER, after=one_hour_ago, oldest_first=False):
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
                messages.append({"role": "user", "username": f"mention_{message.author.name}", "content": content})
                users[f"mention_{message.author.name}"] = message.author.mention

            if len(messages) == HISTORY_TARGET:
                break

        return messages[::-1], users


    async def chatting(self, message: disnake.Message) -> None:
        raw_theme = await self.database.get_theme(message.guild.id)
        theme = GuildTheme.model_validate(raw_theme) if raw_theme else None

        bot_member = message.guild.me
        bot_nick = bot_member.nick
        bot_username = bot_member.name
        bot_mention = self.bot.user.mention

        system = build_system_prompt(theme, bot_nick, bot_username, bot_mention)

        chat_messages, users = await self.get_last_messages(message.channel)

        try:
            response_text = await self.llm_client.complete(system, chat_messages)
        except Exception as e:
            logger.error("LLM call failed for guild %d: %s", message.guild.id, e)
            await message.channel.send(
                "Could not process request. Please try again or contact an administrator."
            )
            return

        for name, mention in users.items():
            response_text = response_text.replace(name, mention)

        await message.channel.send(response_text)


    @commands.slash_command()
    async def chat(self, inter: disnake.ApplicationCommandInteraction) -> None:
        pass


    @chat.sub_command(description="Create thread session to communicate with bot alone")
    async def new_session(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer(ephemeral=True)

        # Get existing thread id or None
        existing_session_id = await self.database.get_thread_id(inter.guild.id, inter.author.id)

        if existing_session_id:
            thread = inter.guild.get_thread(existing_session_id)
            if thread:
                await thread.delete()
            await self.database.remove_thread_id(existing_session_id)

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
        logger.info(
            "Created thread '%s' (id=%d) for user %d in guild %d",
            thread.name,
            thread.id,
            inter.author.id,
            inter.guild.id,
        )

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
    async def end_session(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer(ephemeral=True)

        author_thread_id = await self.database.get_thread_id(inter.guild.id, inter.author.id)

        if not author_thread_id:
            await inter.edit_original_response(f"No thead exists for {inter.author.name} in guild {inter.guild.name}.")
            return

        # Delete user's thread
        thread = inter.guild.get_thread(author_thread_id)
        thread_name = thread.name if thread else str(author_thread_id)
        if thread:
            await thread.delete()
        await self.database.remove_thread_id(author_thread_id)
        logger.info(
            "Deleted thread '%s' for user %d in guild %d",
            thread_name,
            inter.author.id,
            inter.guild.id,
        )

        # If command sent from user's current thread session, do not attempt to send message thorugh it
        if isinstance(inter.channel, disnake.threads.Thread) and inter.channel.id == author_thread_id:
            return
        
        # Send message to channel command was sent in
        await inter.followup.send(f"Deleted thread \"{thread_name}\"")


def setup(bot: commands.InteractionBot) -> None:
    bot.add_cog(Chatbot(bot))