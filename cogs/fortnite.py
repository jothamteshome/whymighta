import random
import requests
from disnake.ext import commands


class Fortnite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Parse API data to find named locations in Fortnite
    def parse_named_locations(self):
        response = requests.get("https://fortnite-api.com/v1/map")
        data = response.json()
        locations = data['data']['pois']

        named_locations = []

        for loc in locations:
            if not 'Athena.Location.POI' in loc['id']:
                continue

            named_locations.append(loc)

        return named_locations


    # Randomly select one of the named locations from a list
    def select_location(self, locations):
        return random.choice(locations)['name'].title()


    @commands.slash_command()
    async def fortnite(self, inter):
        pass


    @fortnite.sub_command(
        description="Select a random drop location in Fortnite")
    async def drop(self, inter):
        named_drops = self.parse_named_locations()

        await inter.response.send_message(f"You should drop at {self.select_location(named_drops)}!")


def setup(bot):
    bot.add_cog(Fortnite(bot))