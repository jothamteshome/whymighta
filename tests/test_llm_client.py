import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from llm.client import AnthropicClient, OpenAIClient, get_llm_client


# ---------------------------------------------------------------------------
# get_llm_client routing
# ---------------------------------------------------------------------------

def test_get_llm_client_no_keys_raises():
    with patch("llm.client.config") as mock_cfg:
        mock_cfg.OPENAI_API_KEY = None
        mock_cfg.ANTHROPIC_API_KEY = None
        with pytest.raises(RuntimeError):
            get_llm_client()


def test_get_llm_client_openai_only():
    with patch("llm.client.config") as mock_cfg:
        mock_cfg.OPENAI_API_KEY = "sk-test"
        mock_cfg.ANTHROPIC_API_KEY = None
        mock_cfg.OPENAI_MODEL = "gpt-4.1-mini"
        assert isinstance(get_llm_client(), OpenAIClient)


def test_get_llm_client_anthropic_only():
    with patch("llm.client.config") as mock_cfg:
        mock_cfg.OPENAI_API_KEY = None
        mock_cfg.ANTHROPIC_API_KEY = "sk-ant-test"
        mock_cfg.ANTHROPIC_MODEL = "claude-haiku-4-5"
        assert isinstance(get_llm_client(), AnthropicClient)


def test_get_llm_client_both_prefers_openai():
    with patch("llm.client.config") as mock_cfg:
        mock_cfg.OPENAI_API_KEY = "sk-test"
        mock_cfg.ANTHROPIC_API_KEY = "sk-ant-test"
        mock_cfg.OPENAI_MODEL = "gpt-4.1-mini"
        assert isinstance(get_llm_client(), OpenAIClient)


# ---------------------------------------------------------------------------
# OpenAIClient.complete
# ---------------------------------------------------------------------------

async def test_openai_client_complete_returns_content():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Hello!"

    mock_openai_instance = MagicMock()
    mock_openai_instance.chat.completions.create = AsyncMock(return_value=mock_response)

    with patch("llm.client.config") as mock_cfg, \
         patch("llm.client.openai.AsyncOpenAI", return_value=mock_openai_instance):
        mock_cfg.OPENAI_API_KEY = "sk-test"
        mock_cfg.OPENAI_MODEL = "gpt-4.1-mini"

        client = OpenAIClient()
        history = [
            {"role": "user", "content": "Hi", "username": "mention_alice"},
            {"role": "assistant", "content": "Hey there"},
        ]
        result = await client.complete("You are helpful.", history)

    assert result == "Hello!"


def test_openai_client_maps_username_to_name():
    """username key on user messages should become name; assistant messages untouched."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Hi"

    mock_openai_instance = MagicMock()
    mock_openai_instance.chat.completions.create = AsyncMock(return_value=mock_response)

    import asyncio

    async def run():
        with patch("llm.client.config") as mock_cfg, \
             patch("llm.client.openai.AsyncOpenAI", return_value=mock_openai_instance):
            mock_cfg.OPENAI_API_KEY = "sk-test"
            mock_cfg.OPENAI_MODEL = "gpt-4.1-mini"
            client = OpenAIClient()
            history = [{"role": "user", "content": "Hi", "username": "mention_alice"}]
            await client.complete("system", history)

    asyncio.get_event_loop().run_until_complete(run())

    call_kwargs = mock_openai_instance.chat.completions.create.call_args.kwargs
    messages = call_kwargs["messages"]
    # system message prepended
    assert messages[0] == {"role": "system", "content": "system"}
    # username mapped to name, not passed through
    user_msg = messages[1]
    assert user_msg.get("name") == "mention_alice"
    assert "username" not in user_msg


# ---------------------------------------------------------------------------
# AnthropicClient.complete
# ---------------------------------------------------------------------------

async def test_anthropic_client_complete_returns_text():
    mock_response = MagicMock()
    mock_response.content[0].text = "Greetings!"

    mock_anthropic_instance = MagicMock()
    mock_anthropic_instance.messages.create = AsyncMock(return_value=mock_response)

    with patch("llm.client.config") as mock_cfg, \
         patch("llm.client.anthropic.AsyncAnthropic", return_value=mock_anthropic_instance):
        mock_cfg.ANTHROPIC_API_KEY = "sk-ant-test"
        mock_cfg.ANTHROPIC_MODEL = "claude-haiku-4-5"

        client = AnthropicClient()
        history = [{"role": "user", "content": "Hello", "username": "mention_bob"}]
        result = await client.complete("Be concise.", history)

    assert result == "Greetings!"


async def test_anthropic_client_embeds_username_in_content():
    mock_response = MagicMock()
    mock_response.content[0].text = "Hi"

    mock_anthropic_instance = MagicMock()
    mock_anthropic_instance.messages.create = AsyncMock(return_value=mock_response)

    with patch("llm.client.config") as mock_cfg, \
         patch("llm.client.anthropic.AsyncAnthropic", return_value=mock_anthropic_instance):
        mock_cfg.ANTHROPIC_API_KEY = "sk-ant-test"
        mock_cfg.ANTHROPIC_MODEL = "claude-haiku-4-5"

        client = AnthropicClient()
        history = [{"role": "user", "content": "Hello", "username": "mention_bob"}]
        await client.complete("system prompt", history)

    call_kwargs = mock_anthropic_instance.messages.create.call_args.kwargs
    # system passed as top-level parameter, not in messages
    assert call_kwargs["system"] == "system prompt"
    messages = call_kwargs["messages"]
    # username embedded as [mention_bob]: prefix in content
    assert "[mention_bob]:" in messages[0]["content"]
    assert "username" not in messages[0]
