import logging
import random

import aiohttp
import disnake
from disnake.ext import commands

logger = logging.getLogger(__name__)


class Fortnite(commands.Cog):
    def __init__(self, bot: commands.InteractionBot) -> None:
        self.bot: commands.InteractionBot = bot

    async def fetch_named_locations(self) -> list[dict]:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://fortnite-api.com/v1/map") as resp:
                resp.raise_for_status()
                data = await resp.json()

        return [
            loc for loc in data["data"]["pois"]
            if "Athena.Location.POI" in loc["id"]
        ]

    def select_location(self, locations: list[dict]) -> str:
        return random.choice(locations)["name"].title()

    @commands.slash_command()
    async def fortnite(self, inter: disnake.ApplicationCommandInteraction) -> None:
        pass

    @fortnite.sub_command(description="Select a random drop location in Fortnite")
    async def drop(self, inter: disnake.ApplicationCommandInteraction) -> None:
        await inter.response.defer()
        named_drops = await self.fetch_named_locations()
        await inter.edit_original_message(f"You should drop at {self.select_location(named_drops)}!")


def setup(bot: commands.InteractionBot) -> None:
    bot.add_cog(Fortnite(bot))
