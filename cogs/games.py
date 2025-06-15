import random
from disnake import Embed
from disnake.ext import commands
from utils.database import Database


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = Database()

    @commands.slash_command()
    async def games(self, inter):
        pass

    @games.sub_command(
        description="Look at all games in the games list")
    async def list(self, inter):
        await inter.response.defer()

        embed = Embed(title="Games List", description=f"\n{'-' * 25}", color=0x9534eb)
        games_list = await self.database.get_all_games_from_list(inter.guild.id)

        for game in games_list:
            embed.add_field(name=f"• {game['game_name']}", value="", inline=False)

        
        await inter.edit_original_message(embed=embed)


    @games.sub_command(
        description="Add game to the games list")
    async def add(self, inter, name: str):
        await inter.response.defer()

        game = await self.database.get_game_from_list(inter.guild.id, name)

        if game:
            await inter.edit_original_message(f"{name} already exists in games list")
        else:
            await self.database.add_game_to_list(inter.guild.id, name)
            await inter.edit_original_message(f"{name} added to games list")


    @games.sub_command(
        description="Remove game from the games list")
    async def remove(self, inter, name: str):
        await inter.response.defer()

        game = await self.database.get_game_from_list(inter.guild.id, name)

        if game: 
            await self.database.remove_game_from_list(inter.guild.id, name)
            await inter.edit_original_message(f"{name} has been removed from games list")
        else:
            await inter.edit_original_message(f"{name} does not exist in games list")


    @games.sub_command(
        description="Randomly select game from the games list")
    async def choose(self, inter):
        await inter.response.defer()

        games = await self.database.get_all_games_from_list(inter.guild.id)

        if not games:
            await inter.edit_original_message(f"Games list is empty. Please add a game before using this command")
        else:
            random_game = random.choice(games)['game_name']
            await inter.edit_original_message(f"You should play {random_game}!")


def setup(bot):
    bot.add_cog(Games(bot))