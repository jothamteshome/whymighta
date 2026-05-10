import sys
from unittest.mock import MagicMock

# Stub core.config before any test module imports it so that modules that do
# `from core.config import config` can be imported in CI without real env vars.
_mock_config = MagicMock()
_mock_config.OPENAI_API_KEY = None
_mock_config.ANTHROPIC_API_KEY = None
_mock_config.OPENAI_MODEL = "gpt-4.1-mini"
_mock_config.ANTHROPIC_MODEL = "claude-haiku-4-5"

sys.modules.setdefault("core.config", MagicMock(config=_mock_config))
