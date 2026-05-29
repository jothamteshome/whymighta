from __future__ import annotations

from typing import Optional

import disnake
from disnake.ext import commands

from utils.theme import DEFAULT_EMBED_COLOR

_EXCLUDED_COGS = {"CogManager", "Admin"}


def build_catalog(bot: commands.InteractionBot, in_dm: bool = False) -> dict[str, list[dict]]:
    """Return {cog_name: [command_info, ...]} for all public commands."""
    catalog: dict[str, list[dict]] = {}

    for cmd in bot.slash_commands.values():
        cog_name = cmd.cog_name or "Other"
        if cog_name in _EXCLUDED_COGS:
            continue
        if in_dm and getattr(cmd, "dm_permission", True) is False:
            continue

        admin_only = (
            cmd.default_member_permissions is not None
            and cmd.default_member_permissions.administrator
        )

        sub_commands = []
        if cmd.children:
            for sub in cmd.children.values():
                options = [
                    {
                        "name": opt.name,
                        "description": opt.description,
                        "required": opt.required,
                        "type": opt.type.name if hasattr(opt.type, "name") else str(opt.type),
                    }
                    for opt in (sub.options or [])
                ]
                sub_commands.append(
                    {"name": sub.name, "description": sub.description or "", "options": options}
                )

        options = []
        if not cmd.children:
            options = [
                {
                    "name": opt.name,
                    "description": opt.description,
                    "required": opt.required,
                    "type": opt.type.name if hasattr(opt.type, "name") else str(opt.type),
                }
                for opt in (cmd.options or [])
            ]

        catalog.setdefault(cog_name, []).append(
            {
                "name": cmd.name,
                "description": cmd.description or "",
                "admin_only": admin_only,
                "sub_commands": sub_commands,
                "options": options,
            }
        )

    return catalog


def _trunc(text: str, limit: int = 97) -> str:
    return text if len(text) <= limit else text[:limit] + "..."


def overview_embed() -> disnake.Embed:
    return disnake.Embed(
        title="whymighta Help",
        description="Select a category below to browse commands.",
        color=DEFAULT_EMBED_COLOR,
    )


def category_embed(cog_name: str, cmds: list[dict]) -> disnake.Embed:
    embed = disnake.Embed(title=f"{cog_name} Commands", color=DEFAULT_EMBED_COLOR)
    for cmd in cmds:
        label = f"/{cmd['name']}"
        desc = cmd["description"] or "No description"
        if cmd["admin_only"]:
            desc += " *(Admin only)*"
        embed.add_field(name=label, value=desc, inline=False)
    return embed


def command_embed(cmd: dict) -> disnake.Embed:
    title = f"/{cmd['name']}"
    if cmd["admin_only"]:
        title += "  ⚙️ Admin only"
    embed = disnake.Embed(
        title=title,
        description=cmd["description"] or "No description.",
        color=DEFAULT_EMBED_COLOR,
    )

    if cmd["sub_commands"]:
        for sub in cmd["sub_commands"]:
            value = sub["description"] or "No description"
            if sub["options"]:
                params = "  ".join(
                    f"`{o['name']}`{'\\*' if o['required'] else ''}" for o in sub["options"]
                )
                value += f"\n**Parameters:** {params}"
            embed.add_field(name=f"/{cmd['name']} {sub['name']}", value=value, inline=False)
        embed.set_footer(text="\\* = required")
    elif cmd["options"]:
        for opt in cmd["options"]:
            req = "Required" if opt["required"] else "Optional"
            embed.add_field(
                name=f"`{opt['name']}` — {req}",
                value=opt["description"] or "No description",
                inline=False,
            )
        embed.set_footer(text="\\* = required")

    return embed


class HelpView(disnake.ui.View):
    def __init__(self, catalog: dict[str, list[dict]]) -> None:
        super().__init__(timeout=120)
        self.catalog = catalog
        self.selected_category: str | None = None
        self.message: Optional[disnake.Message] = None

        category_options = [
            disnake.SelectOption(label=name, value=name)
            for name in sorted(catalog)
        ]
        self._category_select = disnake.ui.StringSelect(
            placeholder="Select a category...",
            options=category_options,
        )
        self._category_select.callback = self._on_category_select
        self.add_item(self._category_select)

    async def _on_category_select(self, inter: disnake.MessageInteraction) -> None:
        self.selected_category = inter.values[0]
        cmds = self.catalog[self.selected_category]

        for child in list(self.children):
            if isinstance(child, disnake.ui.StringSelect) and child is not self._category_select:
                self.remove_item(child)

        command_options = [
            disnake.SelectOption(
                label=f"/{c['name']}",
                value=c["name"],
                description=_trunc(c["description"]) if c["description"] else None,
            )
            for c in cmds
        ]
        cmd_select = disnake.ui.StringSelect(
            placeholder="Select a command...",
            options=command_options,
        )
        cmd_select.callback = self._on_command_select
        self.add_item(cmd_select)

        await inter.response.edit_message(
            embed=category_embed(self.selected_category, cmds),
            view=self,
        )

    async def _on_command_select(self, inter: disnake.MessageInteraction) -> None:
        cmd_name = inter.values[0]
        cmds = self.catalog[self.selected_category]
        cmd = next(c for c in cmds if c["name"] == cmd_name)
        await inter.response.edit_message(embed=command_embed(cmd), view=self)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        if self.message:
            await self.message.edit(view=self)
