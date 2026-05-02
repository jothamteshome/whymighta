import math
from unittest.mock import AsyncMock, MagicMock

import pytest

from utils import xp


def test_check_level_zero():
    assert xp.check_level(0) == 0.0


def test_check_level_known_values():
    # 32 ** (1/5) == 2.0
    assert xp.check_level(32) == pytest.approx(2.0)
    # 243 ** (1/5) == 3.0
    assert xp.check_level(243) == pytest.approx(3.0)


def test_check_level_returns_float():
    assert isinstance(xp.check_level(100), float)


# ---------------------------------------------------------------------------
# announce_level_up
# ---------------------------------------------------------------------------

async def test_announce_level_up_fires_on_new_level():
    """prev=0 -> curr=32 crosses level boundary (floor(0^(1/5))=0, floor(32^(1/5))=2)."""
    db = AsyncMock()
    bot = MagicMock()
    channel = AsyncMock()
    channel.guild.id = 1
    user = MagicMock()
    user.mention = "@user"

    # No bot channel configured — should fall back to supplied channel
    db.get_bot_text_channel_id.return_value = None
    bot.get_channel.return_value = None

    await xp.announce_level_up(db, bot, previous_xp=0, current_xp=32, user=user, channel=channel)

    channel.send.assert_awaited_once()
    assert "Level 2" in channel.send.call_args[0][0]


async def test_announce_level_up_silent_when_no_new_level():
    """prev=1 -> curr=2 does not cross a level boundary."""
    db = AsyncMock()
    bot = MagicMock()
    channel = AsyncMock()
    channel.guild.id = 1
    user = MagicMock()

    db.get_bot_text_channel_id.return_value = None

    await xp.announce_level_up(db, bot, previous_xp=1, current_xp=2, user=user, channel=channel)

    channel.send.assert_not_awaited()


async def test_announce_level_up_uses_bot_channel_when_configured():
    db = AsyncMock()
    bot = MagicMock()
    channel = AsyncMock()
    channel.guild.id = 99
    user = MagicMock()
    user.mention = "@user"

    bot_channel = AsyncMock()
    db.get_bot_text_channel_id.return_value = 42
    bot.get_channel.return_value = bot_channel

    await xp.announce_level_up(db, bot, previous_xp=0, current_xp=32, user=user, channel=channel)

    bot_channel.send.assert_awaited_once()
    channel.send.assert_not_awaited()


# ---------------------------------------------------------------------------
# give_message_xp
# ---------------------------------------------------------------------------

async def test_give_message_xp_updates_score():
    db = AsyncMock()
    bot = MagicMock()

    message = MagicMock()
    message.author.id = 1
    message.guild.id = 2
    message.mentions = []
    message.attachments = []
    message.content = "hello"  # 5 chars
    message.channel = AsyncMock()
    message.channel.guild.id = 2

    db.current_user_score.return_value = 10

    await xp.give_message_xp(db, bot, message, catching_up=True)

    # score = 10 (prev) + 0 (mentions) + 0 (attachments) + 5 (content) = 15
    db.update_user_score.assert_awaited_once_with(1, 2, 15)
    db.update_last_message_sent.assert_awaited_once()


async def test_give_message_xp_no_level_announce_when_catching_up():
    """When catching_up=True, announce_level_up must not be called."""
    db = AsyncMock()
    bot = MagicMock()

    message = MagicMock()
    message.author.id = 1
    message.guild.id = 2
    message.mentions = []
    message.attachments = []
    message.content = "a" * 1000  # big enough to trigger level-up math
    message.channel = AsyncMock()

    db.current_user_score.return_value = 0
    # bot.get_channel should NOT be called
    bot.get_channel = MagicMock()

    await xp.give_message_xp(db, bot, message, catching_up=True)

    bot.get_channel.assert_not_called()


async def test_give_message_xp_counts_mentions_and_attachments():
    db = AsyncMock()
    bot = MagicMock()

    message = MagicMock()
    message.author.id = 5
    message.guild.id = 6
    message.mentions = [MagicMock(), MagicMock()]   # 2 * 5 = 10
    message.attachments = [MagicMock()]             # 1 * 10 = 10
    message.content = "hi"                          # 2
    message.channel = AsyncMock()
    message.channel.guild.id = 6

    db.current_user_score.return_value = 0
    db.get_bot_text_channel_id.return_value = None

    await xp.give_message_xp(db, bot, message, catching_up=True)

    db.update_user_score.assert_awaited_once_with(5, 6, 22)
