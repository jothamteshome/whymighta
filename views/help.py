from __future__ import annotations

import math
from typing import Optional

import disnake
from disnake.ext import commands

from utils.theme import DEFAULT_EMBED_COLOR

_EXCLUDED_COGS = {"CogManager", "Admin", "Help"}
PAGE_SIZE = 6


def build_catalog(bot: commands.InteractionBot, in_dm: bool = False) -> dict[str, list[dict]]:
    catalog: dict[str, list[dict]] = {}

    for cmd in bot.all_slash_commands.values():
        cog_name = cmd.cog_name or "Other"
        if cog_name in _EXCLUDED_COGS:
            continue
        cmd_contexts = getattr(cmd, "contexts", None)
        if in_dm and cmd_contexts is not None and not cmd_contexts.bot_dm:
            continue

        admin_only = (
            cmd.default_member_permissions is not None
            and cmd.default_member_permissions.administrator
        )

        if cmd.children:
            for sub in cmd.children.values():
                catalog.setdefault(cog_name, []).append({
                    "path": f"/{cmd.name} {sub.name}",
                    "description": sub.description or "",
                    "admin_only": admin_only,
                })
        else:
            catalog.setdefault(cog_name, []).append({
                "path": f"/{cmd.name}",
                "description": cmd.description or "",
                "admin_only": admin_only,
            })

    return catalog


def overview_embed(catalog: dict[str, list[dict]]) -> disnake.Embed:
    num_categories = len(catalog)
    num_commands = sum(len(cmds) for cmds in catalog.values())
    overview = disnake.Embed(
        title="Commands for whymighta",
        color=DEFAULT_EMBED_COLOR,
    )

    overview.add_field(
        name="**» Help menu**",
        value=(
            f"I've got `{num_categories}` categories and "
            f"`{num_commands}` commands for you to explore."
        )
    )

    categories = sorted(catalog)
    col_width = max(len(c) for c in categories) + 4
    rows = [
        "".join(c.ljust(col_width) for c in categories[i : i + 3])
        for i in range(0, len(categories), 3)
    ]
    overview.add_field(
        name="**» Categories**",
        value=f"```\n{chr(10).join(rows)}\n```",
        inline=False,
    )
    return overview


def category_embed(cog_name: str, cmds: list[dict], page: int, total_pages: int) -> disnake.Embed:
    start = page * PAGE_SIZE
    page_cmds = cmds[start : start + PAGE_SIZE]
    embed = disnake.Embed(
        title=f"Commands ({len(cmds)})",
        color=DEFAULT_EMBED_COLOR,
    )
    for entry in page_cmds:
        name = entry["path"] + ("  ⚙️" if entry["admin_only"] else "")
        embed.add_field(name=f"`{name}`", value=entry["description"] or "No description", inline=False)
    if total_pages > 1:
        embed.set_footer(text=f"Page {page + 1} of {total_pages}")
    return embed


class HelpView(disnake.ui.View):
    def __init__(self, catalog: dict[str, list[dict]]) -> None:
        super().__init__(timeout=120)
        self.catalog = catalog
        self.current_category: str | None = None
        self.page: int = 0
        self.message: Optional[disnake.Message] = None
        self._rebuild_components()

    def _total_pages(self) -> int:
        if self.current_category is None:
            return 1
        return max(1, math.ceil(len(self.catalog[self.current_category]) / PAGE_SIZE))

    def _rebuild_components(self) -> None:
        self.clear_items()

        select = disnake.ui.StringSelect(
            placeholder="Select a category...",
            options=[
                disnake.SelectOption(label=name, value=name, default=(name == self.current_category))
                for name in sorted(self.catalog)
            ],
            row=0,
        )
        select.callback = self._on_category_select
        self.add_item(select)

        total = self._total_pages()

        if self.current_category is not None:
            prev = disnake.ui.Button(
                label="◀", style=disnake.ButtonStyle.secondary, row=1, disabled=(self.page == 0)
            )
            prev.callback = self._on_prev
            self.add_item(prev)

        close = disnake.ui.Button(label="✕ Close", style=disnake.ButtonStyle.secondary, row=1)
        close.callback = self._on_close
        self.add_item(close)

        if self.current_category is not None:
            nxt = disnake.ui.Button(
                label="▶", style=disnake.ButtonStyle.secondary, row=1, disabled=(self.page >= total - 1)
            )
            nxt.callback = self._on_next
            self.add_item(nxt)

    async def _on_category_select(self, inter: disnake.MessageInteraction) -> None:
        self.current_category = inter.values[0]
        self.page = 0
        self._rebuild_components()
        cmds = self.catalog[self.current_category]
        await inter.response.edit_message(
            embed=category_embed(self.current_category, cmds, self.page, self._total_pages()),
            view=self,
        )

    async def _on_prev(self, inter: disnake.MessageInteraction) -> None:
        self.page -= 1
        self._rebuild_components()
        cmds = self.catalog[self.current_category]
        await inter.response.edit_message(
            embed=category_embed(self.current_category, cmds, self.page, self._total_pages()),
            view=self,
        )

    async def _on_next(self, inter: disnake.MessageInteraction) -> None:
        self.page += 1
        self._rebuild_components()
        cmds = self.catalog[self.current_category]
        await inter.response.edit_message(
            embed=category_embed(self.current_category, cmds, self.page, self._total_pages()),
            view=self,
        )

    async def _on_close(self, inter: disnake.MessageInteraction) -> None:
        await inter.response.defer()
        await inter.delete_original_response()

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        if self.message:
            await self.message.edit(view=self)
