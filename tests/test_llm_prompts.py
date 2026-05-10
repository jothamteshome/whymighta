import pytest

from llm.prompts import DEFAULT_SYSTEM_PROMPT, build_system_prompt
from models.theme import GuildTheme

BOT_USERNAME = "TestBot"
BOT_MENTION = "<@123456>"


def make_theme(**kwargs) -> GuildTheme:
    return GuildTheme(names=["Alice", "Bob"], **kwargs)


def test_no_theme_no_nick_contains_default_prompt():
    result = build_system_prompt(None, None, BOT_USERNAME, BOT_MENTION)
    assert DEFAULT_SYSTEM_PROMPT in result


def test_bot_mention_rule_always_present():
    result = build_system_prompt(None, None, BOT_USERNAME, BOT_MENTION)
    assert f"Never mention anyone with the mention tag {BOT_MENTION}" in result


def test_no_theme_with_nick_embody_block():
    result = build_system_prompt(None, "Sparky", BOT_USERNAME, BOT_MENTION)
    assert "Sparky" in result
    assert "embody" in result.lower()


def test_no_theme_nick_same_as_username_no_nick_block():
    # nick_is_set requires nick != username
    result = build_system_prompt(None, BOT_USERNAME, BOT_USERNAME, BOT_MENTION)
    assert "embody" not in result.lower()
    assert "identity" not in result.lower()


def test_theme_roleplay_with_nick_identity_block():
    theme = make_theme(title="Fantasy", description="Epic quests.", roleplay=True)
    result = build_system_prompt(theme, "Gandalf", BOT_USERNAME, BOT_MENTION)
    assert "Gandalf" in result
    assert "identity" in result.lower()


def test_theme_no_roleplay_with_nick_no_roleplay_block():
    theme = make_theme(title="Fantasy", roleplay=False)
    result = build_system_prompt(theme, "Gandalf", BOT_USERNAME, BOT_MENTION)
    assert "Gandalf" in result
    assert "Do not attempt to roleplay" in result


def test_theme_title_appears_in_prompt():
    theme = make_theme(title="Sci-Fi")
    result = build_system_prompt(theme, "R2D2", BOT_USERNAME, BOT_MENTION)
    assert "Sci-Fi" in result


def test_theme_description_appears_in_prompt():
    theme = make_theme(description="A space adventure.")
    result = build_system_prompt(theme, "R2D2", BOT_USERNAME, BOT_MENTION)
    assert "A space adventure." in result


def test_theme_without_title_or_description_no_theme_line():
    theme = make_theme(roleplay=True)
    result = build_system_prompt(theme, "Gandalf", BOT_USERNAME, BOT_MENTION)
    assert "The server's current theme is" not in result
