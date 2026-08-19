import disnake, logging, random
from aiohttp import ClientResponseError
from core.config import config
from disnake import Embed
from disnake.ext import commands
from database.manager import Database
from utils import fortnite as utils_fortnite
from utils import minecraft as utils_minecraft
from utils.constants import DEFAULT_EMBED_COLOR

logger = logging.getLogger(__name__)


class Games(commands.Cog):
    category_display_name = "Games"
    category_emoji = "🎮"

    def __init__(self, bot: commands.InteractionBot) -> None:
        self.bot: commands.InteractionBot = bot
        self.database: Database = bot.db

    @commands.slash_command(
            description="Game list and selection commands", 
            contexts=disnake.InteractionContextTypes(guild=True)
        )
    async def games(self, inter: disnake.ApplicationCommandInteraction) -> None:
        pass

    @games.sub_command(description="Look at all games in the games list")
    async def list(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()

        embed = Embed(title="Games List", description=f"\n{'-' * 25}", color=DEFAULT_EMBED_COLOR)
        games_list = await self.database.get_all_games_from_list(inter.guild.id)

        for game in games_list:
            embed.add_field(name=f"• {game['game_name']}", value="", inline=False)

        await inter.edit_original_message(embed=embed)

    @games.sub_command(description="Add game to the games list")
    async def add(
        self, 
        inter: disnake.ApplicationCommandInteraction, 
        name: str = commands.Param(description="Game to add to the list")
    ) -> None:
        await inter.response.defer()

        game = await self.database.get_game_from_list(inter.guild.id, name)

        if game:
            await inter.edit_original_message(f"{name} already exists in games list")
        else:
            await self.database.add_game_to_list(inter.guild.id, name)
            await inter.edit_original_message(f"{name} added to games list")

    @games.sub_command(description="Remove game from the games list")
    async def remove(
        self, 
        inter: disnake.ApplicationCommandInteraction, 
        name: str = commands.Param(description="Game to remove from the list")
    ) -> None:
        await inter.response.defer()

        game = await self.database.get_game_from_list(inter.guild.id, name)

        if game:
            await self.database.remove_game_from_list(inter.guild.id, name)
            await inter.edit_original_message(f"{name} has been removed from games list")
        else:
            await inter.edit_original_message(f"{name} does not exist in games list")

    @games.sub_command(description="Randomly select game from the games list")
    async def choose(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()

        games = await self.database.get_all_games_from_list(inter.guild.id)

        if not games:
            await inter.edit_original_message(
                "Games list is empty. Please add a game before using this command"
            )
        else:
            random_game = random.choice(games)["game_name"]
            await inter.edit_original_message(f"You should play {random_game}!")

    @commands.slash_command(description="Fortnite utilities")
    async def fortnite(self, inter: disnake.ApplicationCommandInteraction) -> None:
        pass

    @fortnite.sub_command(description="Select a random drop location in Fortnite")
    async def drop(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()
        named_drops = await utils_fortnite.fetch_named_locations()
        await inter.edit_original_message(f"You should drop at {utils_fortnite.select_location(named_drops)}!")

    @commands.slash_command(description="Minecraft utilities")
    async def minecraft(self, inter: disnake.ApplicationCommandInteraction) -> None:
        pass

    @minecraft.sub_command(description="Check status of the Minecraft servers")
    async def status(self, inter: disnake.ApplicationCommandInteraction) -> None:
        if not config.MINECRAFT_API_TOKEN or not config.MINECRAFT_API_URL:
            await inter.response.send_message("Minecraft controls are not configured on this bot.", ephemeral=True)
            return

        await inter.response.defer()

        try:
            statuses = await utils_minecraft.get_status()
        except ClientResponseError:
            await inter.edit_original_message("Could not reach the Minecraft API. Please try again later.")
            return

        embed = Embed(title="Minecraft Server Status", color=DEFAULT_EMBED_COLOR)
        for name, info in statuses.items():
            embed.add_field(
                name=name.title(),
                value=f"{utils_minecraft.format_state(info['state'])}\n{info['hostname']}",
                inline=True,
            )

        await inter.edit_original_message(embed=embed)


    @minecraft.sub_command(description="Start a Minecraft server")
    async def start(
        self, inter: disnake.ApplicationCommandInteraction,
        server: str = commands.Param(choices=["vanilla", "modded", "datapack"]),
    ) -> None:
        if not config.MINECRAFT_API_TOKEN or not config.MINECRAFT_API_URL:
            await inter.response.send_message("Minecraft controls are not configured on this bot.", ephemeral=True)
            return

        await inter.response.defer()

        try:
            result = await utils_minecraft.start_server(server)
        except ClientResponseError:
            await inter.edit_original_message("Could not reach the Minecraft API. Please try again later.")
            return

        await inter.edit_original_message(
            f"**{result['hostname']}** is starting up. Server should be available within the next 60 seconds."
        )


    @minecraft.sub_command(description="Stop a Minecraft server (owner only)")
    async def stop(
        self, inter: disnake.ApplicationCommandInteraction,
        server: str = commands.Param(choices=["vanilla", "modded", "datapack"]),
    ) -> None:
        if not await self.bot.is_owner(inter.author):
            await inter.response.send_message("Only the bot owner can stop the Minecraft server.", ephemeral=True)
            return

        if not config.MINECRAFT_API_TOKEN or not config.MINECRAFT_API_URL:
            await inter.response.send_message("Minecraft controls are not configured on this bot.", ephemeral=True)
            return

        await inter.response.defer()

        try:
            result = await utils_minecraft.stop_server(server)
        except ClientResponseError:
            await inter.edit_original_message("Could not reach the Minecraft API. Please try again later.")
            return

        await inter.edit_original_message(
            f"**{result['hostname']}** is shutting down."
        )



def setup(bot: commands.InteractionBot) -> None:
    bot.add_cog(Games(bot))