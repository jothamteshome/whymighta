import logging
import math
import time

import disnake
from disnake import ApplicationCommandInteraction, Embed
from disnake.ext import commands

from database.manager import Database
from utils import xp
from views.leaderboard import LeaderboardView
from utils.theme import DEFAULT_EMBED_COLOR

logger = logging.getLogger(__name__)


class Utilities(commands.Cog):
    category_display_name = "Utilities"
    category_emoji = "🛠️"

    def __init__(self, bot: commands.InteractionBot) -> None:
        self.bot: commands.InteractionBot = bot
        self.database: Database = bot.db

    @commands.slash_command(description="Check the latency of the bot")
    async def ping(self, inter: ApplicationCommandInteraction) -> None:
        before = time.monotonic()
        embed = Embed(title=":information_source: | Pong!", description="\n", color=DEFAULT_EMBED_COLOR)
        await inter.response.send_message(embed=embed)
        latency = (time.monotonic() - before) * 1000
        embed.add_field(name="Latency", value=str(int(latency)) + "ms", inline=False)
        embed.add_field(name="API", value=str(int(self.bot.latency * 1000)) + "ms", inline=False)
        await inter.edit_original_response(embed=embed)

    @commands.slash_command(description="Check your level and XP progress")
    async def level(self, inter: ApplicationCommandInteraction) -> None:
        await inter.response.defer()

        global_xp = await self.database.current_global_score(inter.author.id)
        global_level_floor = math.floor(xp.check_level(global_xp))
        global_progress = int(round(xp.check_level(global_xp) - global_level_floor, 2) * 100)
        global_bar = math.floor(global_progress / 10)

        embed = Embed(title=f"{inter.author.name}'s Level Progress", description="\n", color=DEFAULT_EMBED_COLOR)
        embed.add_field(
            name=f"Global — {global_progress}% to Level {global_level_floor + 1}",
            value=(global_bar * "🔵") + ((10 - global_bar) * "⚪"),
            inline=False,
        )

        if inter.guild_id is not None:
            guild_xp = await self.database.current_guild_score(inter.author.id, inter.guild_id)
            guild_level_floor = math.floor(xp.check_level(guild_xp))
            guild_progress = int(round(xp.check_level(guild_xp) - guild_level_floor, 2) * 100)
            guild_bar = math.floor(guild_progress / 10)
            embed.add_field(
                name=f"Server — {guild_progress}% to Level {guild_level_floor + 1}",
                value=(guild_bar * "🔵") + ((10 - guild_bar) * "⚪"),
                inline=False,
            )

        await inter.edit_original_message(embed=embed)

    @commands.slash_command(description="View the server XP leaderboard", contexts=disnake.InteractionContextTypes(guild=True))
    async def leaderboard(self, inter: ApplicationCommandInteraction) -> None:
        await inter.response.defer()

        rows = await self.database.get_leaderboard(inter.guild_id)

        if not rows:
            embed = Embed(title="Leaderboard", description="No XP data yet.", color=DEFAULT_EMBED_COLOR)
            await inter.edit_original_message(embed=embed)
            return

        view = LeaderboardView(rows, inter.guild)
        await inter.edit_original_message(embed=view.get_embed(), view=view)
        view.message = await inter.original_message()

def setup(bot: commands.InteractionBot) -> None:
    bot.add_cog(Utilities(bot))
