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
    await inter.response.defer()

    embed = disnake.Embed(title="Games List", description=f"\n{'-' * 25}", color=0x9534eb)
    games_list = await whymightaDatabase.get_all_games_from_list(inter.guild.id)

    for game in games_list:
        embed.add_field(name=f"• {game['game_name']}", value="", inline=False)

    
    await inter.edit_original_message(embed=embed)


@games.sub_command(
    description="Add game to the games list")
async def add(inter, name: str):
    await inter.response.defer()

    game = await whymightaDatabase.get_game_from_list(inter.guild.id, name)

    if game:
        await inter.edit_original_message(f"{name} already exists in games list")
    else:
        await whymightaDatabase.add_game_to_list(inter.guild.id, name)
        await inter.edit_original_message(f"{name} added to games list")


@games.sub_command(
    description="Remove game from the games list")
async def remove(inter, name: str):
    await inter.response.defer()

    game = await whymightaDatabase.get_game_from_list(inter.guild.id, name)

    if game: 
        await whymightaDatabase.remove_game_from_list(inter.guild.id, name)
        await inter.edit_original_message(f"{name} has been removed from games list")
    else:
        await inter.edit_original_message(f"{name} does not exist in games list")


@games.sub_command(
    description="Randomly select game from the games list")
async def choose(inter):
    await inter.response.defer()

    games = await whymightaDatabase.get_all_games_from_list(inter.guild.id)

    if not games:
        await inter.edit_original_message(f"Games list is empty. Please add a game before using this command")
    else:
        random_game = random.choice(games)['game_name']
        await inter.edit_original_message(f"You should play {random_game}!")

    