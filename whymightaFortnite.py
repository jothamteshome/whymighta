import requests
import random
import whymightaGlobalVariables

# Parse API data to find named locations in Fortnite
def parseNamedLocations():
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
def selectLocation(locations):
    return random.choice(locations)['name'].title()


@whymightaGlobalVariables.bot.slash_command()
async def fortnite(inter):
    pass



@fortnite.sub_command(
    description="Select a random drop location in Fortnite")
async def drop(inter):
    named_drops = parseNamedLocations()

    await inter.response.send_message(f"You should drop at {selectLocation(named_drops)}!")