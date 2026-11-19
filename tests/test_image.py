import io
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import disnake
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer
from PIL import Image

from utils import image as utils_image


def _png_bytes(size=(256, 256)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGBA", size, (255, 0, 0, 255)).save(buf, "PNG")
    return buf.getvalue()


def _mock_session(body: bytes) -> MagicMock:
    """Build a stand-in for aiohttp.ClientSession whose get() returns `body`."""
    resp = MagicMock()
    resp.read = AsyncMock(return_value=body)

    get_cm = MagicMock()
    get_cm.__aenter__ = AsyncMock(return_value=resp)
    get_cm.__aexit__ = AsyncMock(return_value=False)

    session = MagicMock()
    session.get.return_value = get_cm

    session_cm = MagicMock()
    session_cm.__aenter__ = AsyncMock(return_value=session)
    session_cm.__aexit__ = AsyncMock(return_value=False)
    return session_cm


async def test_imprison_member_returns_png_file():
    member = MagicMock()
    member.display_avatar.url = "http://example.test/avatar.png"

    with patch.object(utils_image.aiohttp, "ClientSession", return_value=_mock_session(_png_bytes())):
        result = await utils_image.imprison_member(member)

    assert isinstance(result, disnake.File)
    assert result.filename == "image.png"
    out = Image.open(result.fp)
    assert out.format == "PNG"
    assert out.size == (256, 256)


@pytest.fixture
async def server():
    async def ok(request):
        return web.Response(body=b"image-bytes")

    app = web.Application()
    app.router.add_get("/ok", ok)
    srv = TestServer(app)
    await srv.start_server()
    yield srv
    await srv.close()


async def test_fetch_image_bytes_returns_body(server):
    assert await utils_image.fetch_image_bytes(str(server.make_url("/ok"))) == b"image-bytes"


async def test_fetch_image_bytes_raises_on_404(server):
    with pytest.raises(aiohttp.ClientResponseError) as exc:
        await utils_image.fetch_image_bytes(str(server.make_url("/missing")))
    assert exc.value.status == 404
