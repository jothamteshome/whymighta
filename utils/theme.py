import aiohttp, asyncio, disnake, logging, random
from database.manager import Database
from models.theme import GuildTheme
from typing import Optional
from utils import image as utils_image


logger = logging.getLogger(__name__)


async def get_guild_theme(database: Database, guild_id: int) -> Optional[GuildTheme]:
    """Fetch the stored theme for a guild and return a validated GuildTheme, or None."""
    raw = await database.get_theme(guild_id)
    return GuildTheme.model_validate(raw) if raw else None


def add_theme_fields(embed: disnake.Embed, theme: GuildTheme, bot_nick: str) -> None:
    """Add standard theme fields to an embed in-place."""
    embed.add_field(name="Theme Title", value=theme.title or "Not set", inline=False)
    embed.add_field(name="Description", value=(theme.description or "Not set")[:100], inline=False)
    embed.add_field(name="Names in Pool", value=str(len(theme.names)), inline=True)
    embed.add_field(name="Roleplay", value="On" if theme.roleplay else "Off", inline=True)
    embed.add_field(name="Bot's Character", value=bot_nick, inline=True)


async def assign_nicknames(guild: disnake.Guild, names: list[str]) -> list[tuple[str, str]]:
    """Randomly assign nicknames from `names` to guild members.

    Returns a list of (member_name, intended_nick) pairs that were skipped due to
    role hierarchy or permission errors.
    """
    new_nicks = list(names)
    random.shuffle(new_nicks)

    skipped: list[tuple[str, str]] = []

    for member in guild.members:
        new_nick = new_nicks.pop()

        if member != guild.me and (member == guild.owner or guild.me.top_role <= member.top_role):
            logger.debug("Skipping %s (role hierarchy)", member.name)
            skipped.append((member.name, new_nick))
            continue

        try:
            await member.edit(nick=new_nick)
            logger.debug("Assigned %s -> %s", member.name, new_nick)
            await asyncio.sleep(1.1)
        except disnake.errors.Forbidden as e:
            logger.debug("No permission for %s: %s", member.name, e)
            skipped.append((member.name, new_nick))
        except disnake.errors.HTTPException as e:
            logger.warning("HTTP error for %s: %s %s", member.name, e.status, e.text)
            skipped.append((member.name, new_nick))

    return skipped


async def apply_guild_appearance(guild: disnake.Guild, theme: GuildTheme) -> list[str]:
    """Apply server name and icon from a theme.

    Returns a list of feedback strings describing the outcome of each attempted change.
    An empty list means no appearance fields were set on the theme.
    """
    feedback: list[str] = []

    if theme.title:
        try:
            await guild.edit(name=theme.title)
            feedback.append(f"Server name updated to **{theme.title}**.")
        except disnake.errors.Forbidden:
            feedback.append("Could not update server name (missing Manage Server permission).")
        except disnake.errors.HTTPException as e:
            feedback.append(f"Could not update server name: {e.text}")

    if theme.icon_url:
        try:
            icon_bytes = await utils_image.fetch_image_bytes(theme.icon_url)
            await guild.edit(icon=icon_bytes)
            feedback.append("Server icon updated.")
        except aiohttp.ClientError as e:
            feedback.append(f"Could not fetch server icon: {e}")
        except disnake.errors.Forbidden:
            feedback.append("Could not update server icon (missing Manage Server permission).")
        except disnake.errors.HTTPException as e:
            feedback.append(f"Could not update server icon: {e.text}")

    return feedback
