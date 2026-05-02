from unittest.mock import AsyncMock, MagicMock

from utils import message_modes


def _make_message(content: str = "hello", attachments: list = None, guild_id: int = 1, author_id: int = 10):
    message = MagicMock()
    message.content = content
    message.attachments = attachments or []
    message.guild.id = guild_id
    message.author.id = author_id
    message.channel = AsyncMock()
    return message


# ---------------------------------------------------------------------------
# mock_user
# ---------------------------------------------------------------------------

async def test_mock_user_does_nothing_when_disabled():
    db = AsyncMock()
    db.query_mock.return_value = False
    message = _make_message()

    await message_modes.mock_user(db, message)

    message.channel.send.assert_not_awaited()


async def test_mock_user_spongebob_plain_text():
    db = AsyncMock()
    db.query_mock.return_value = True
    message = _make_message(content="hello")

    await message_modes.mock_user(db, message)

    message.channel.send.assert_awaited_once_with("hElLo")


async def test_mock_user_passthrough_url():
    db = AsyncMock()
    db.query_mock.return_value = True
    message = _make_message(content="https://example.com")

    await message_modes.mock_user(db, message)

    message.channel.send.assert_awaited_once_with("https://example.com")


async def test_mock_user_attachment_with_text():
    db = AsyncMock()
    db.query_mock.return_value = True
    attachment = MagicMock()
    message = _make_message(content="look", attachments=[attachment])

    await message_modes.mock_user(db, message)

    calls = message.channel.send.await_args_list
    assert len(calls) == 2
    assert calls[0].args[0] == "lOoK"
    assert calls[1].args[0] is attachment


async def test_mock_user_attachment_no_text():
    db = AsyncMock()
    db.query_mock.return_value = True
    attachment = MagicMock()
    message = _make_message(content="", attachments=[attachment])

    await message_modes.mock_user(db, message)

    message.channel.send.assert_awaited_once_with(attachment)


# ---------------------------------------------------------------------------
# binarize_message
# ---------------------------------------------------------------------------

async def test_binarize_message_does_nothing_when_disabled():
    db = AsyncMock()
    db.query_binary.return_value = False
    message = _make_message()

    await message_modes.binarize_message(db, message)

    message.channel.send.assert_not_awaited()


async def test_binarize_message_plain_text():
    db = AsyncMock()
    db.query_binary.return_value = True
    # 'a' = 01100001
    message = _make_message(content="a")

    await message_modes.binarize_message(db, message)

    message.channel.send.assert_awaited_once_with("01100001")


async def test_binarize_message_passthrough_url():
    db = AsyncMock()
    db.query_binary.return_value = True
    message = _make_message(content="https://example.com")

    await message_modes.binarize_message(db, message)

    message.channel.send.assert_awaited_once_with("https://example.com")


async def test_binarize_message_attachment_with_text():
    db = AsyncMock()
    db.query_binary.return_value = True
    attachment = MagicMock()
    # 'a' = 01100001
    message = _make_message(content="a", attachments=[attachment])

    await message_modes.binarize_message(db, message)

    calls = message.channel.send.await_args_list
    assert len(calls) == 2
    assert calls[0].args[0] == "01100001"
    assert calls[1].args[0] is attachment
