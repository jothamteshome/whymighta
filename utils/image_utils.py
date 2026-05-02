import asyncio
import io

import aiohttp
import disnake
from PIL import Image


async def imprison_member(member: disnake.Member) -> disnake.File:
    """Overlay prison bars over a member's avatar and return a disnake File."""
    MAX_IMG_SIZE = 1024

    # Fetch avatar bytes asynchronously
    async with aiohttp.ClientSession() as session:
        async with session.get(member.display_avatar.url) as resp:
            avatar_bytes = await resp.read()

    def _compose() -> bytes:
        avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")

        prison_bars = Image.open("images/prison_bars.png")

        prison_bar_mid = prison_bars.width // 2
        left = prison_bar_mid - MAX_IMG_SIZE // 2
        right = prison_bar_mid + MAX_IMG_SIZE // 2
        prison_bars = prison_bars.crop((left, 0, right, MAX_IMG_SIZE))

        width_ratio = avatar.width / prison_bars.width
        height = int(prison_bars.height * width_ratio)
        prison_bars = prison_bars.resize((avatar.width, height))

        imprisoned = Image.alpha_composite(avatar, prison_bars)
        imprisoned = Image.alpha_composite(imprisoned, prison_bars)

        buf = io.BytesIO()
        imprisoned.save(buf, "PNG")
        return buf.getvalue()

    image_bytes = await asyncio.get_event_loop().run_in_executor(None, _compose)
    return disnake.File(fp=io.BytesIO(image_bytes), filename="image.png")
