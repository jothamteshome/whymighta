from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, field_validator


class GuildTheme(BaseModel):
    names: list[str]
    title: Optional[str] = None
    description: Optional[str] = None
    roleplay: bool = False
    icon_url: Optional[str] = None

    @field_validator("icon_url", mode="before")
    @classmethod
    def validate_icon_url(cls, v: object) -> Optional[str]:
        if v is None:
            return None
        try:
            return str(AnyHttpUrl(str(v)))
        except Exception:
            return None
