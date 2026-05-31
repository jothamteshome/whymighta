from __future__ import annotations

import math

import disnake

from utils import xp
from utils.constants import DEFAULT_EMBED_COLOR

PAGE_SIZE = 10
_MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}


def _build_pages(rows: list, names: dict[int, str], sort: str) -> list[str]:
    if not rows:
        return ["No XP data yet."]

    score_key = "guild_chat_score" if sort == "guild" else "global_chat_score"

    entries = []
    for rank, row in enumerate(rows, start=1):
        name = names.get(row["user_id"], str(row["user_id"]))
        score = row[score_key]
        level = math.floor(xp.check_level(score))
        prefix = _MEDALS.get(rank, f"`{rank}.`")
        entries.append(f"{prefix} **{name}**\n> Lv {level} · {score:,} XP")

    pages = []
    for i in range(0, len(entries), PAGE_SIZE):
        pages.append("\n".join(entries[i : i + PAGE_SIZE]))
    return pages


class LeaderboardView(disnake.ui.View):
    def __init__(self, rows: list, guild_name: str, names: dict[int, str]) -> None:
        super().__init__(timeout=None)
        self.guild_name = guild_name
        self.current_page = 0
        self.sort = "guild"

        rows_global = sorted(rows, key=lambda r: r["global_chat_score"], reverse=True)
        self.pages_guild = _build_pages(rows, names, "guild")
        self.pages_global = _build_pages(rows_global, names, "global")

        self._update_button_states()

    @property
    def _active_pages(self) -> list[str]:
        return self.pages_guild if self.sort == "guild" else self.pages_global

    @property
    def total_pages(self) -> int:
        return len(self._active_pages)

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
        sort_label = "Guild" if self.sort == "guild" else "Global"
        return disnake.Embed(
            title=f"{self.guild_name} Leaderboard — {sort_label} Score",
            description=self._active_pages[self.current_page],
            color=DEFAULT_EMBED_COLOR,
        )

    @disnake.ui.button(label="◀", style=disnake.ButtonStyle.secondary)
    async def prev_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.current_page -= 1
        self._update_button_states()
        await inter.response.edit_message(
            content=f"Page {self.current_page + 1} of {self.total_pages}",
            embed=self.get_embed(),
            view=self,
        )

    @disnake.ui.button(label="Guild Sort", style=disnake.ButtonStyle.primary)
    async def guild_sort_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.sort = "guild"
        self.current_page = 0
        self._update_button_states()
        await inter.response.edit_message(
            content=f"Page {self.current_page + 1} of {self.total_pages}",
            embed=self.get_embed(),
            view=self,
        )

    @disnake.ui.button(label="Global Sort", style=disnake.ButtonStyle.secondary)
    async def global_sort_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.sort = "global"
        self.current_page = 0
        self._update_button_states()
        await inter.response.edit_message(
            content=f"Page {self.current_page + 1} of {self.total_pages}",
            embed=self.get_embed(),
            view=self,
        )

    @disnake.ui.button(label="▶", style=disnake.ButtonStyle.secondary)
    async def next_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction) -> None:
        self.current_page += 1
        self._update_button_states()
        await inter.response.edit_message(
            content=f"Page {self.current_page + 1} of {self.total_pages}",
            embed=self.get_embed(),
            view=self,
        )
