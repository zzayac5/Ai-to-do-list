from __future__ import annotations

import json
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from backend.app.llm.client import LLMClient, get_llm_client
from backend.app.llm.prompts import build_system_prompt
from backend.app.llm.tool_handlers import ToolContext, execute_tool
from backend.app.llm.tool_schemas import get_tool_schemas
from backend.app.schemas import ChatRequest, ChatResponse, ToolResult


def _to_openai_messages(request: ChatRequest) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": build_system_prompt(today=date.today().isoformat())}
    ]

    if request.history:
        for m in request.history:
            # Don't allow clients to override system instructions.
            if m.role == "system":
                continue
            messages.append({"role": m.role, "content": m.content})

    messages.append({"role": "user", "content": request.message})
    return messages


def run_chat(db: Session, *, request: ChatRequest, llm_client: LLMClient | None = None) -> ChatResponse:
    """
    Minimal tool-calling loop:
    - send user message + tools
    - if model calls tools, execute and feed results back
    - repeat until the model returns a normal assistant message
    """
    client = llm_client or get_llm_client()
    tools = get_tool_schemas()
    messages = _to_openai_messages(request)

    tool_results: list[ToolResult] = []
    ctx = ToolContext(db=db, user_id=request.user_id)

    for _step in range(6):
        model_msg = client.complete(messages=messages, tools=tools)

        assistant_payload: dict[str, Any] = {"role": "assistant", "content": model_msg.content or ""}
        if model_msg.tool_calls:
            assistant_payload["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": tc.arguments},
                }
                for tc in model_msg.tool_calls
            ]

        messages.append(assistant_payload)

        if not model_msg.tool_calls:
            return ChatResponse(reply=(model_msg.content or "").strip(), tool_results=tool_results)

        for tc in model_msg.tool_calls:
            result = execute_tool(ctx, name=tc.name, arguments_json=tc.arguments)
            tool_results.append(
                ToolResult(
                    name=tc.name,
                    ok=bool(result.get("ok", False)),
                    result=result.get("result"),
                    error=result.get("error"),
                )
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result, default=str),
                }
            )

    return ChatResponse(
        reply="I got stuck while using tools. Try rephrasing or ask to list tasks.",
        tool_results=tool_results,
    )

