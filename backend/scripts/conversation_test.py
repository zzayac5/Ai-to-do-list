from __future__ import annotations

import os
from pprint import pprint

from sqlalchemy.orm import Session

from backend.app.db.init_db import init_db
from backend.app.db.session import SessionLocal
from backend.app.llm.client import MockLLMClient
from backend.app.llm.orchestrator import run_chat
from backend.app.schemas import ChatRequest


def main() -> None:
    # Force offline mode so this test runs without API keys/network.
    os.environ["MOCK_LLM"] = "true"

    init_db()

    db: Session = SessionLocal()
    try:
        turns = [
            "Tomorrow I need to call the bank about my car loan.",
            "Also add: schedule a dentist appointment next week.",
            "List my tasks.",
            "Prioritize my tasks.",
        ]

        print("Running mock conversation...\n")
        history = []
        client = MockLLMClient()
        for t in turns:
            req = ChatRequest(message=t, history=history, session_id="demo")
            resp = run_chat(db, request=req, llm_client=client)

            print(f"USER: {t}")
            print(f"ASSISTANT: {resp.reply}")
            if resp.tool_results:
                print("TOOLS:")
                for tr in resp.tool_results:
                    print(f"  - {tr.name} ok={tr.ok}")
            print()

            # Minimal history: keep only user+assistant content (skip tool chatter).
            history.extend(
                [
                    {"role": "user", "content": t},
                    {"role": "assistant", "content": resp.reply},
                ]
            )

        print("Done.\n")
        print("Tip: set OPENAI_API_KEY and unset MOCK_LLM to try the real model.")

    finally:
        db.close()


if __name__ == "__main__":
    main()

