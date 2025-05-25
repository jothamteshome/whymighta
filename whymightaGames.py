import random
import disnake
import time

import whymightaDatabase
import whymightaGlobalVariables


@whymightaGlobalVariables.bot.slash_command()
async def games(inter):
    pass

@games.sub_command(
    description="Look at all games in the games list")
async def list(inter):
    embed = disnake.Embed(title="Games List", description=f"\n{'-' * 25}", color=0x9534eb)
    games_list = whymightaDatabase.getAllGamesFromList(inter.guild.id)

    for game in games_list:
        embed.add_field(name=f"• {game['game_name']}", value="", inline=False)

    
    await inter.response.send_message(embed=embed)


@games.sub_command(
    description="Add game to the games list")
async def add(inter, name: str):
    game = whymightaDatabase.getGameFromList(inter.guild.id, name)

    if game:
        await inter.response.send_message(f"{name} already exists in games list")
    else:
        whymightaDatabase.addGameToList(inter.guild.id, name)
        await inter.response.send_message(f"{name} added to games list")


@games.sub_command(
    description="Remove game from the games list")
async def remove(inter, name: str):
    game = whymightaDatabase.getGameFromList(inter.guild.id, name)

    if game: 
        whymightaDatabase.removeGameFromList(inter.guild.id, name)
        await inter.response.send_message(f"{name} has been removed from games list")
    else:
        await inter.response.send_message(f"{name} does not exist in games list")


@games.sub_command(
    description="Randomly select game from the games list")
async def choose(inter):
    games = whymightaDatabase.getAllGamesFromList(inter.guild.id)

    if not games:
        await inter.response.send_message(f"Games list is empty. Please add a game before using this command")
    else:
        random_game = random.choice(games)['game_name']
        await inter.response.send_message(f"You should play {random_game}!")

    