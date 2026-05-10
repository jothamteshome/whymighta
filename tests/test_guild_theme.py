import pytest
from pydantic import ValidationError

from models.theme import GuildTheme


def test_valid_minimal():
    theme = GuildTheme.model_validate({"names": ["Alice", "Bob"]})
    assert theme.names == ["Alice", "Bob"]
    assert theme.roleplay is False
    assert theme.title is None
    assert theme.description is None
    assert theme.icon_url is None


def test_valid_full():
    data = {
        "names": ["Alice"],
        "title": "Fantasy",
        "description": "A fantasy server.",
        "roleplay": True,
        "icon_url": "https://example.com/icon.png",
    }
    theme = GuildTheme.model_validate(data)
    assert theme.title == "Fantasy"
    assert theme.description == "A fantasy server."
    assert theme.roleplay is True
    assert theme.icon_url == "https://example.com/icon.png"


def test_missing_names_raises():
    with pytest.raises(ValidationError):
        GuildTheme.model_validate({"title": "Oops"})


def test_names_not_list_raises():
    with pytest.raises(ValidationError):
        GuildTheme.model_validate({"names": "not-a-list"})


def test_extra_fields_ignored():
    # Pydantic ignores unknown fields by default
    theme = GuildTheme.model_validate({"names": ["Alice"], "unknown_field": "ignored"})
    assert theme.names == ["Alice"]
