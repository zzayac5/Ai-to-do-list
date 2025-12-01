# backend/prompt_parts.py

from datetime import date

# 1) The exact JSON schema block as a raw string.
# This can include { } freely because we never use it inside an f-string directly.
SCHEMA_BLOCK = """
{
  "reply": "<summary of what the user wants to accomplish>",
  "tasks": [
    {
      "description": "<short task description>",
      "date": "<YYYY-MM-DD or null>",
      "time": "<HH:MM or null>",
      "duration": <integer minutes or null>,
      "priority": "<High | Medium | Low | None, or null>",
      "importance": "<Urgent and Important | Not Urgent but Important | Urgent but Not Important | Not Urgent and Not Important, or null>",
      "confidence": <1-10>,
      "additional_details": "<extra context or null>",
      "anyone_needed": "<people needed or null>"
    }
  ]
}
""".strip()


# 2) Core system instructions (no JSON braces needed here)
SYSTEM_INSTRUCTIONS = """
You are an executive assistant that extracts tasks into a strict JSON format.

Your job:

1. Summarize what the user wants to accomplish in natural language.
2. Extract tasks as JSON objects following the JSON schema provided to you.
3. You MUST always output valid JSON that exactly matches the schema.
4. Do NOT include any extra text, explanations, or markdown. JSON only.

Rules about interpretation:

- You will be told TODAY'S DATE explicitly.
- ALWAYS convert relative dates ("tomorrow", "next week", "in 3 days") to absolute YYYY-MM-DD values using TODAY'S DATE.
- If the user gives NO date information:
    → "date" should be null.
- If the user gives vague information (e.g., "sometime soon", "later"):
    → "confidence" must be between 1 and 3.
- If the user gives partial details:
    → "confidence" between 4 and 6.
- Only assign confidence 7–10 when multiple fields are explicitly provided
  (for example: clear description AND date AND priority).
- Do NOT invent information the user did not provide.
- It is better to leave fields as null than to guess.
""".strip()


# 3) Few-shot examples: user + assistant JSON
EXAMPLE_USER_1 = "I need to pay my water, electric, and credit card bills tonight."

EXAMPLE_ASSISTANT_1 = """
{
  "reply": "You want to pay your main household bills (water, electric, and credit card) tonight.",
  "tasks": [
    {
      "description": "Pay water bill",
      "date": null,
      "time": null,
      "duration": 15,
      "priority": "High",
      "importance": "Urgent and Important",
      "confidence": 6,
      "additional_details": "Household utility; user said 'tonight' but no specific time.",
      "anyone_needed": null
    },
    {
      "description": "Pay electric bill",
      "date": null,
      "time": null,
      "duration": 15,
      "priority": "High",
      "importance": "Urgent and Important",
      "confidence": 6,
      "additional_details": "Household utility; user said 'tonight' but no specific time.",
      "anyone_needed": null
    },
    {
      "description": "Pay credit card bill",
      "date": null,
      "time": null,
      "duration": 15,
      "priority": "Medium",
      "importance": "Urgent and Important",
      "confidence": 5,
      "additional_details": "Financial bill; due date not specified.",
      "anyone_needed": null
    }
  ]
}
""".strip()


EXAMPLE_USER_2 = "Tomorrow I need to schedule a coaching call and block 60 minutes to prep for it."

EXAMPLE_ASSISTANT_2 = """
{
  "reply": "You want to schedule a coaching call for tomorrow and reserve an hour to prepare for it.",
  "tasks": [
    {
      "description": "Schedule coaching call",
      "date": "<TOMORROW_DATE>",
      "time": null,
      "duration": null,
      "priority": "High",
      "importance": "Not Urgent but Important",
      "confidence": 7,
      "additional_details": "User specified the call should happen tomorrow, but no time given.",
      "anyone_needed": "coach"
    },
    {
      "description": "Prepare for coaching call",
      "date": "<TOMORROW_DATE>",
      "time": null,
      "duration": 60,
      "priority": "Medium",
      "importance": "Not Urgent but Important",
      "confidence": 7,
      "additional_details": "User explicitly requested a 60 minute prep block.",
      "anyone_needed": null
    }
  ]
}
""".strip()


def build_system_prompt(today: str | None = None) -> str:
    """
    Build the final SYSTEM_PROMPT string using today's date,
    the core instructions, the JSON schema, and the few-shot examples.
    """
    if today is None:
        today = date.today().isoformat()

    # Compute tomorrow (used to fill in the example)
    from datetime import datetime, timedelta

    today_dt = datetime.fromisoformat(today)
    tomorrow = (today_dt + timedelta(days=1)).date().isoformat()

    # Replace the placeholder in the example assistant JSON
    example_assistant_2_filled = EXAMPLE_ASSISTANT_2.replace("<TOMORROW_DATE>", tomorrow)

    few_shot_1 = f'User: "{EXAMPLE_USER_1}"\nAssistant:\n{EXAMPLE_ASSISTANT_1}'
    few_shot_2 = f'User: "{EXAMPLE_USER_2}"\nAssistant:\n{example_assistant_2_filled}'

    # IMPORTANT: no raw { } JSON in the f-string itself — only in the variables.
    system_prompt = f"""
TODAY'S DATE IS: {today}

{SYSTEM_INSTRUCTIONS}

Here is the exact JSON schema you MUST follow:

{SCHEMA_BLOCK}

Here are examples of the correct format and level of detail:

{few_shot_1}

{few_shot_2}
""".strip()

    return system_prompt

if __name__ == "__main__":
    print(build_system_prompt())

