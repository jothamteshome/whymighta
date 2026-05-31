import json
import logging
from io import BytesIO
from typing import Optional

import disnake
from disnake.ext import commands
from pydantic import ValidationError

from database.manager import Database
from models.theme import GuildTheme
from utils.theme_utils import (
    add_theme_fields,
    apply_guild_appearance,
    assign_nicknames,
    get_guild_theme,
)

logger = logging.getLogger(__name__)


class Server(commands.Cog):
    category_display_name = "Server"
    category_emoji = "⚙️"

    def __init__(self, bot: commands.InteractionBot) -> None:
        self.bot: commands.InteractionBot = bot
        self.database: Database = bot.db

    # ---- /server ----

    @commands.slash_command(
        description="Show bot status and configuration for this server",
        default_member_permissions=disnake.Permissions(administrator=True),
        contexts=disnake.InteractionContextTypes(guild=True),
    )
    async def server(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()

        bot_channel_id = await self.database.get_bot_text_channel_id(inter.guild.id)
        if bot_channel_id:
            channel = inter.guild.get_channel(bot_channel_id)
            channel_value = channel.mention if channel else f"Unknown ({bot_channel_id})"
        else:
            channel_value = "Not set"

        mock, binary = await self.database.get_guild_config(inter.guild.id)
        theme = await get_guild_theme(self.database, inter.guild.id)

        embed = disnake.Embed(title="Bot Status", color=0x9534eb)
        embed.add_field(name="Bot Channel", value=channel_value, inline=False)
        embed.add_field(name="Mock Mode", value="On" if mock else "Off", inline=True)
        embed.add_field(name="Binary Mode", value="On" if binary else "Off", inline=True)

        if theme:
            bot_nick = inter.guild.me.nick or "None assigned"
            add_theme_fields(embed, theme, bot_nick)
        else:
            embed.add_field(name="Theme", value="Not set", inline=False)

        await inter.edit_original_message(embed=embed)

    # ---- /theme ----

    @commands.slash_command(
        default_member_permissions=disnake.Permissions(administrator=True),
        contexts=disnake.InteractionContextTypes(guild=True),
    )
    async def theme(self, inter: disnake.ApplicationCommandInteraction) -> None:
        pass

    @theme.sub_command(description="Randomly updates server nicknames based on those found in uploaded file")
    async def apply(self, inter: disnake.ApplicationCommandInteraction, file: disnake.Attachment) -> None:
        await inter.response.defer()

        if "application/json" not in file.content_type:
            await inter.edit_original_message("File must be a json")
            return

        fp = BytesIO()
        logger.debug("Starting file download")
        await file.save(fp)
        fp.seek(0)

        try:
            theme_data = GuildTheme.model_validate(json.load(fp))
        except json.JSONDecodeError:
            await inter.edit_original_message("Could not parse file: invalid JSON.")
            return
        except ValidationError as e:
            await inter.edit_original_message(f"Invalid theme format: {e}")
            return

        members = inter.guild.members

        if len(theme_data.names) < len(members):
            await inter.edit_original_message(
                f"Please provide enough names to allocate one for each member in server "
                f"({len(members) - len(theme_data.names)} more required)"
            )
            return

        logger.debug("JSON loaded: %d names, %d members", len(theme_data.names), len(members))

        skipped = await assign_nicknames(inter.guild, theme_data.names)
        await inter.edit_original_message("Random nicknames have been assigned")

        if skipped:
            lines = "\n".join(f"`{name}` — {nick}" for name, nick in skipped)
            await inter.channel.send(f"**Could not assign nicknames for:**\n{lines}")

        appearance_feedback = await apply_guild_appearance(inter.guild, theme_data)
        for message in appearance_feedback:
            await inter.channel.send(message)

        try:
            await self.database.set_theme(inter.guild.id, theme_data.model_dump())
        except Exception as e:
            logger.error("Failed to save theme for guild %d: %s", inter.guild.id, e)
            await inter.channel.send("Nicknames were assigned but the theme could not be saved to the database.")

    @theme.sub_command(description="Get current server nicknames in json format")
    async def export(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()

        server_names: dict[str, Optional[str]] = {
            member.name: member.nick for member in inter.guild.members
        }

        byte_fp = BytesIO(json.dumps(server_names).encode())
        server_names_file = disnake.File(fp=byte_fp, filename="server_nicknames_dump.json")

        await inter.edit_original_response(content="", file=server_names_file)

    @theme.sub_command(description="Clear the current theme")
    async def clear(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()
        await self.database.clear_theme(inter.guild.id)
        await inter.edit_original_message(
            "Theme cleared. New members will need to be renamed manually until a new theme is applied."
        )

    @theme.sub_command(description="Toggle roleplay mode for the current theme")
    async def roleplay(
        self,
        inter: disnake.ApplicationCommandInteraction,
        enabled: str = commands.Param(choices=["on", "off"]),
    ) -> None:
        await inter.response.defer()

        theme_data = await get_guild_theme(self.database, inter.guild.id)
        if not theme_data:
            await inter.edit_original_message("No theme is currently set.")
            return

        updated = theme_data.model_copy(update={"roleplay": enabled == "on"})
        await self.database.set_theme(inter.guild.id, updated.model_dump())
        status = "enabled" if updated.roleplay else "disabled"
        await inter.edit_original_message(f"Roleplay is now {status}.")

    # ---- /bot_channel ----

    @commands.slash_command(
        name="bot_channel",
        default_member_permissions=disnake.Permissions(administrator=True),
        contexts=disnake.InteractionContextTypes(guild=True),
    )
    async def channel(self, inter: disnake.ApplicationCommandInteraction) -> None:
        pass

    @channel.sub_command(description="Set a new channel as the default bot channel")
    async def set(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()
        await self.database.set_bot_text_channel_id(inter.guild.id, inter.channel.id)
        logger.info("Bot channel set to %d in guild %d", inter.channel.id, inter.guild.id)
        await inter.edit_original_message(f"Bot messages will now appear in {inter.channel.name}!")

    @channel.sub_command(description="Get name of current bot channel")
    async def show(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()

        bot_channel_id = await self.database.get_bot_text_channel_id(inter.guild.id)
        current_channel: Optional[str] = None

        for ch in inter.guild.text_channels:
            if ch.id == bot_channel_id:
                current_channel = ch.name
                break

        if current_channel is not None:
            await inter.edit_original_message(f"Current bot text channel is #{current_channel}")
        else:
            await inter.edit_original_message("No channel has been set as the bot channel")

    # ---- /toggle ----

    @commands.slash_command(
        default_member_permissions=disnake.Permissions(administrator=True),
        contexts=disnake.InteractionContextTypes(guild=True),
    )
    async def toggle(self, inter: disnake.ApplicationCommandInteraction) -> None:
        pass

    @toggle.sub_command(description="Toggles the mock status of the bot")
    async def mock(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()
        enabled = await self.database.toggle_mock(inter.guild_id)
        logger.info("Mock toggled to %s in guild %d", enabled, inter.guild_id)
        await inter.edit_original_message("Mocking has been enabled" if enabled else "Mocking has been disabled")

    @toggle.sub_command(description="Toggles the binary writing status of the bot")
    async def binary(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()
        enabled = await self.database.toggle_binary(inter.guild_id)
        logger.info("Binary toggled to %s in guild %d", enabled, inter.guild_id)
        await inter.edit_original_message("Binary has been enabled" if enabled else "Binary has been disabled")

    # ---- /purge ----

    @commands.slash_command(
        description="Clear up to 100 messages from the current channel at once",
        default_member_permissions=disnake.Permissions(administrator=True),
        contexts=disnake.InteractionContextTypes(guild=True),
    )
    async def purge(self, inter: disnake.ApplicationCommandInteraction, number: int = 5) -> None:
        if number < 1 or number > 100:
            await inter.response.send_message("Number must be between 1 and 100.")
            return
        message_str = "message" if number == 1 else "messages"
        logger.info(
            "Purge: %d messages in channel %d (guild %d) by user %d",
            number,
            inter.channel.id,
            inter.guild.id,
            inter.author.id,
        )
        await inter.response.send_message(f"{inter.author} cleared {number} {message_str} from the channel")
        await inter.channel.purge(limit=number + 1)


def setup(bot: commands.InteractionBot) -> None:
    bot.add_cog(Server(bot))
