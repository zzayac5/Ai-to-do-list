from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

from backend.app.core.config import settings


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: str


@dataclass(frozen=True)
class LLMMessage:
    content: str | None
    tool_calls: list[ToolCall]


class LLMClient:
    def complete(self, *, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> LLMMessage:
        raise NotImplementedError


class OpenAIChatCompletionsClient(LLMClient):
    def __init__(self) -> None:
        if settings.openai_api_key:
            os.environ["OPENAI_API_KEY"] = settings.openai_api_key
        try:
            from openai import OpenAI  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError("openai package is required to use the real LLM client.") from e

        self._client = OpenAI()

    def complete(self, *, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> LLMMessage:
        resp = self._client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.2,
        )
        msg = resp.choices[0].message

        tool_calls: list[ToolCall] = []
        if getattr(msg, "tool_calls", None):
            for tc in msg.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=tc.function.arguments,
                    )
                )

        return LLMMessage(content=msg.content, tool_calls=tool_calls)


class MockLLMClient(LLMClient):
    """
    Offline, deterministic "model" used for local testing without network/API keys.

    It demonstrates the tool-calling loop by:
    - calling `create_task` for most user inputs
    - calling `list_tasks` if the user asks to list/show tasks
    - returning a short confirmation after tools run
    """

    def complete(self, *, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> LLMMessage:
        _ = tools  # schema unused in mock

        last = messages[-1]
        role = last.get("role")
        content = (last.get("content") or "").strip()

        # After tool execution, respond normally.
        if role == "tool":
            try:
                payload = json.loads(content)
            except Exception:
                payload = None
            if isinstance(payload, dict) and payload.get("ok") and payload.get("result"):
                return LLMMessage(content="Saved. Want me to prioritize your list or ask clarifying questions?", tool_calls=[])
            return LLMMessage(content="I tried a tool but it failed. Want to try again?", tool_calls=[])

        if role == "user":
            low = content.lower()
            if any(k in low for k in ["list", "show tasks", "what's next", "what are my tasks"]):
                return LLMMessage(content=None, tool_calls=[ToolCall(id="mock_call_1", name="list_tasks", arguments="{}")])
            if any(k in low for k in ["prioritize", "prioritise", "priority"]):
                return LLMMessage(
                    content=None,
                    tool_calls=[ToolCall(id="mock_call_1", name="prioritize_tasks", arguments="{}")],
                )

            # Minimal task creation: store the raw message as a title.
            args = {"title": content[:200]}
            return LLMMessage(
                content=None,
                tool_calls=[ToolCall(id="mock_call_1", name="create_task", arguments=json.dumps(args))],
            )

        return LLMMessage(content="How can I help?", tool_calls=[])


def get_llm_client() -> LLMClient:
    if (os.getenv("MOCK_LLM", "") or "").lower() in {"1", "true", "yes", "y"}:
        return MockLLMClient()
    if not settings.openai_api_key:
        # Default to mock so the app boots without keys.
        return MockLLMClient()
    return OpenAIChatCompletionsClient()
