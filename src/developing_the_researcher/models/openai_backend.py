"""Optional OpenAI backend for validation runs when USE_OPENAI is set."""
from __future__ import annotations

import os

from ..config import OPENAI_MODEL, USE_OPENAI


def _use_openai() -> bool:
    return USE_OPENAI or os.environ.get("USE_OPENAI", "").lower() in ("1", "true", "yes")


class OpenAIGenerate:
    """Wrapper that implements the same interface as CommitteeLoader.generate for OpenAI API."""

    def __init__(self, model: str | None = None):
        self.model = model or OPENAI_MODEL
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI()
            except ImportError:
                raise ImportError("openai package required. pip install openai")
        return self._client

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        do_sample: bool = True,
    ) -> str:
        """Generate response via OpenAI API. Same interface as CommitteeLoader.generate."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        kwargs = {"model": self.model, "messages": messages, "max_tokens": max_new_tokens}
        if do_sample:
            kwargs["temperature"] = temperature
        else:
            kwargs["temperature"] = 0
        resp = self.client.chat.completions.create(**kwargs)
        return (resp.choices[0].message.content or "").strip()


def get_generate_fn():
    """Return generate function: OpenAI if USE_OPENAI, else None (caller uses CommitteeLoader)."""
    if _use_openai():
        gen = OpenAIGenerate()
        return gen.generate
    return None
