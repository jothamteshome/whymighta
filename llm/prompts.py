from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.theme import GuildTheme

DEFAULT_SYSTEM_PROMPT = (
    "You are a friendly, lighthearted presence in a Discord server. "
    "Keep your tone casual and conversational, like a friend in a group chat. "
    "Keep responses short and snappy. Limit emoji use. "
    "If mentioning a specific user, use the mention_ prefix with their username "
    "and remove any <, >, or @ characters. "
    "Disregard earlier messages that don't relate to the most recent one — "
    "weight the most recent message most heavily."
)


def build_system_prompt(
    theme: "GuildTheme | None",
    bot_nick: str | None,
    bot_username: str,
    bot_mention: str,
) -> str:
    prompt = DEFAULT_SYSTEM_PROMPT
    prompt += f"\n\nNever mention anyone with the mention tag {bot_mention}."

    has_theme = theme is not None
    nick_is_set = bool(bot_nick and bot_nick != bot_username)

    if has_theme and (theme.title or theme.description):
        theme_line = "The server's current theme is"
        if theme.title:
            theme_line += f" {theme.title}."
        if theme.description:
            theme_line += f" {theme.description}."
        prompt += f"\n\n{theme_line}"

    if has_theme and theme.roleplay and nick_is_set:
        prompt += (
            f'\n\nYou have been assigned the identity "{bot_nick}". '
            f"Speak and behave like {bot_nick} would in casual conversation — "
            "lean into the character naturally, but don't overdo it. "
            "You're still helpful if someone genuinely needs something."
        )
    elif has_theme and nick_is_set:
        prompt += (
            f'\n\nYou have been given the name "{bot_nick}" as part of this theme. '
            "Do not attempt to roleplay as this name."
        )
    elif not has_theme and nick_is_set:
        prompt += (
            f'\n\nYou have been given the name "{bot_nick}". '
            "You may embody this name lightly in conversation."
        )

    return prompt
