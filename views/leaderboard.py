from __future__ import annotations

import math
from typing import Optional

import disnake

from utils import xp
from utils.theme import DEFAULT_EMBED_COLOR

PAGE_SIZE = 10


def _build_pages(rows: list, guild: disnake.Guild, sort: str) -> list[str]:
    lines = []
    for rank, row in enumerate(rows, start=1):
        member = guild.get_member(row["user_id"])
        name = member.display_name if member else "Former Member"
        guild_score = row["guild_chat_score"]
        global_score = row["global_chat_score"]
        active_score = guild_score if sort == "guild" else global_score
        level = math.floor(xp.check_level(active_score))
        lines.append(
            f"`{rank}.` **{name}** — Lv.{level} │ Guild: {guild_score:,} XP │ Global: {global_score:,} XP"
        )

    if not lines:
        return ["No XP data yet."]

    pages = []
    for i in range(0, len(lines), PAGE_SIZE):
        pages.append("\n".join(lines[i : i + PAGE_SIZE]))
    return pages


class LeaderboardView(disnake.ui.View):
    def __init__(self, rows: list, guild: disnake.Guild) -> None:
        super().__init__(timeout=60)
        self.guild_name = guild.name
        self.current_page = 0
        self.sort = "guild"
        self.message: Optional[disnake.Message] = None

        rows_global = sorted(rows, key=lambda r: r["global_chat_score"], reverse=True)
        self.pages_guild = _build_pages(rows, guild, "guild")
        self.pages_global = _build_pages(rows_global, guild, "global")

        self._update_button_states()

    @property
    def _active_pages(self) -> list[str]:
        return self.pages_guild if self.sort == "guild" else self.pages_global

    def _update_button_states(self) -> None:
        pages = self._active_pages
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page >= len(pages) - 1
        self.guild_sort_button.style = (
            disnake.ButtonStyle.primary if self.sort == "guild" else disnake.ButtonStyle.secondary
        )
        self.global_sort_button.style = (
            disnake.ButtonStyle.primary if self.sort == "global" else disnake.ButtonStyle.secondary
        )

    def get_embed(self) -> disnake.Embed:
        pages = self._active_pages
        sort_label = "Guild" if self.sort == "guild" else "Global"
        embed = disnake.Embed(
            title=f"{self.guild_name} Leaderboard — {sort_label} Score",
            description=pages[self.current_page],
            color=DEFAULT_EMBED_COLOR,
        )
        embed.set_footer(text=f"Page {self.current_page + 1}/{len(pages)}")
        return embed

    @disnake.ui.button(label="◀ Prev", style=disnake.ButtonStyle.secondary)
    async def prev_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.current_page -= 1
        self._update_button_states()
        await inter.response.edit_message(embed=self.get_embed(), view=self)

    @disnake.ui.button(label="Next ▶", style=disnake.ButtonStyle.secondary)
    async def next_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.current_page += 1
        self._update_button_states()
        await inter.response.edit_message(embed=self.get_embed(), view=self)

    @disnake.ui.button(label="Guild Sort", style=disnake.ButtonStyle.primary)
    async def guild_sort_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.sort = "guild"
        self.current_page = 0
        self._update_button_states()
        await inter.response.edit_message(embed=self.get_embed(), view=self)

    @disnake.ui.button(label="Global Sort", style=disnake.ButtonStyle.secondary)
    async def global_sort_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.sort = "global"
        self.current_page = 0
        self._update_button_states()
        await inter.response.edit_message(embed=self.get_embed(), view=self)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        if self.message:
            await self.message.edit(view=self)
