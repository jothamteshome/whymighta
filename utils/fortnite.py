import aiohttp, random

async def fetch_named_locations() -> list[dict]:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://fortnite-api.com/v1/map") as resp:
                resp.raise_for_status()
                data = await resp.json()

        return [
            loc for loc in data["data"]["pois"]
            if "Athena.Location.POI" in loc["id"]
        ]

def select_location(locations: list[dict]) -> str:
    return random.choice(locations)["name"].title()