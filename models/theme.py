from typing import Optional

from pydantic import BaseModel


class GuildTheme(BaseModel):
    names: list[str]
    title: Optional[str] = None
    description: Optional[str] = None
    roleplay: bool = False
    icon_url: Optional[str] = None
