import logging
from abc import ABC, abstractmethod

import anthropic
import openai

from core.config import config

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    @abstractmethod
    async def complete(self, system: str, history: list[dict]) -> str:
        ...


class OpenAIClient(LLMClient):
    async def complete(self, system: str, history: list[dict]) -> str:
        messages = [{"role": "system", "content": system}]
        for msg in history:
            m = {"role": msg["role"], "content": msg["content"]}
            if msg["role"] == "user" and "username" in msg:
                m["name"] = msg["username"]
            messages.append(m)

        client = openai.AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=messages,
        )
        return response.choices[0].message.content


class AnthropicClient(LLMClient):
    async def complete(self, system: str, history: list[dict]) -> str:
        messages = []
        for msg in history:
            content = msg["content"]
            if msg["role"] == "user" and "username" in msg:
                content = f"[{msg['username']}]: {content}"
            messages.append({"role": msg["role"], "content": content})

        client = anthropic.AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
        response = await client.messages.create(
            model=config.ANTHROPIC_MODEL,
            max_tokens=1024,
            system=system,
            messages=messages,
        )
        return response.content[0].text


def get_llm_client() -> LLMClient:
    if config.OPENAI_API_KEY:
        logger.info("Using OpenAI client (model: %s)", config.OPENAI_MODEL)
        return OpenAIClient()
    if config.ANTHROPIC_API_KEY:
        logger.info("Using Anthropic client (model: %s)", config.ANTHROPIC_MODEL)
        return AnthropicClient()
    raise RuntimeError(
        "No LLM API key configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY."
    )
