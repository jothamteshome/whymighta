import aiohttp, logging
from core.config import config

logger = logging.getLogger(__name__)


def get_headers() -> dict:
    return {"x-api-key": config.MINECRAFT_API_TOKEN}


async def get_status() -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{config.MINECRAFT_API_URL}/status", headers=get_headers()) as resp:
            resp.raise_for_status()
            return await resp.json()


async def start_server(name: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{config.MINECRAFT_API_URL}/start", headers=get_headers(), json={"server": name}) as resp:
            text = await resp.text()
            logger.info(f"Status: {resp.status}, Body: {text}")
            resp.raise_for_status()
            return await resp.json()


async def stop_server(name: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{config.MINECRAFT_API_URL}/stop", headers=get_headers(), json={"server": name}) as resp:
            text = await resp.text()
            logger.info(f"Status: {resp.status}, Body: {text}")
            resp.raise_for_status()
            return await resp.json()