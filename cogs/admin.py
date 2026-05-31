import disnake, logging
from disnake.ext import commands
from utils import admin as utils_admin
from utils.constants import DEFAULT_EMBED_COLOR

logger = logging.getLogger(__name__)


class Admin(commands.Cog):
    category_display_name = "Admin"
    category_emoji = "🔧"

    def __init__(self, bot: commands.InteractionBot) -> None:
        self.bot: commands.InteractionBot = bot

    @commands.slash_command(contexts=disnake.InteractionContextTypes(guild=True))
    @commands.is_owner()
    async def admin(self, inter: disnake.ApplicationCommandInteraction) -> None:
        pass

    @admin.sub_command(description="Clears all guild application commands")
    async def clear_guild_commands(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer(ephemeral=True)
        guilds = await utils_admin.clear_guild_commands(self.bot)

        embed = disnake.Embed(title="Guilds Cleared", description=f"\n{'-' * 25}", color=DEFAULT_EMBED_COLOR)
        for guild in guilds:
            embed.add_field(name=f"• {guild.id} - {guild.name}", value="", inline=False)

        await inter.edit_original_message(embed=embed)

    @admin.sub_command(description="Clears all global application commands — use sync_global_commands to re-register")
    async def clear_global_commands(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer(ephemeral=True)
        await self.bot.bulk_overwrite_global_commands([])
        await inter.edit_original_message(
            "All global commands cleared. Run /admin sync_global_commands to re-register."
        )

    @admin.sub_command(description="Push current local commands to Discord — no restart needed")
    async def sync_global_commands(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer(ephemeral=True)
        global_cmds, _ = self.bot._ordered_unsynced_commands(None)
        try:
            await self.bot.bulk_overwrite_global_commands(global_cmds)
        except Exception as e:
            await inter.edit_original_message(f"Sync failed: {e}")
            return
        cmds = await self.bot.fetch_global_commands()
        self.bot.slash_command_ids = {
            c.name: c.id
            for c in cmds
            if c.type == disnake.ApplicationCommandType.chat_input
        }
        await inter.edit_original_message(
            f"Synced {len(global_cmds)} commands to Discord. "
            "Mentions updated. Changes may take up to 1 hour to propagate."
        )


def setup(bot: commands.InteractionBot) -> None:
    bot.add_cog(Admin(bot))
