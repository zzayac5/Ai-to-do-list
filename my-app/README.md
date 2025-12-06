# Ai Enabled To Do Chat Agent\

AI-Enabled To-Do List
A FastAPI-powered backend + lightweight frontend that turns natural language into structured tasks using OpenAI models.
Overview
This project is an AI-driven task extraction system.
Users can type plain-language inputs such as:
"I need to pay my bills and schedule a coaching call tomorrow."
The backend uses structured prompting and the OpenAI API to convert this into highly structured JSON tasks including:
description
date (with inferred “today/tomorrow/this week”)
time
duration
priority
importance category
confidence score
additional details
people required
The goal: automate planning, prioritization, and future scheduling based on short user messages.

AI-Enabled To-Do List
A FastAPI-powered backend + lightweight frontend that turns natural language into structured tasks using OpenAI models.
Overview
This project is an AI-driven task extraction system.
Users can type plain-language inputs such as:
"I need to pay my bills and schedule a coaching call tomorrow."
The backend uses structured prompting and the OpenAI API to convert this into highly structured JSON tasks including:
description
date (with inferred “today/tomorrow/this week”)
time
duration
priority
importance category
confidence score
additional details
people required
The goal: automate planning, prioritization, and future scheduling based on short user messages.


my-app/
│
├── backend/
│   ├── main.py             # FastAPI app + OpenAI request handling
│   ├── schemas.py          # Pydantic models for validation
│   ├── database.py         # SQLite wrapper (placeholder)
│   ├── prompt_parts.py     # System prompt, examples, and JSON schema template
│
├── frontend/
│   ├── index.html          # UI for sending messages
│   ├── app.js              # JS fetch call to backend
│   ├── styles.css          # Basic styling
│
├── .venv/                  # Virtual environment (ignored in git)
├── .env                    # API keys (ignored in git)
├── .gitignore              # Ignore rules
├── requirements.txt        # Python dependencies
└── README.md               # This file



Getting Started
1. Clone the repository

git clone https://github.com/zzayac5/Ai-to-do-list.git
cd Ai-to-do-list/my-app

2. Create and activate the virtual environment

python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies

pip install -r requirements.txt

4. Add your .env file
Create a file named .env in the project root:

OPENAI_API_KEY=your_key_here

5. Run the backend
From inside my-app/:

uvicorn backend.main:app --reload --port 8000

The API will be live at:
http://127.0.0.1:8000

6. Run the frontend
Open frontend/index.html in your browser
—or—
use a VS Code Live Server extension.

Endpoint
POST /chat
Example Request Body
{
  "message": "I need to pay my bills and schedule a coaching call tomorrow."
}
Example Response (simplified)
{
  "reply": "You want to pay your bills tomorrow and schedule a coaching call.",
  "tasks": [
    {
      "description": "Pay bills",
      "date": "2025-12-01",
      "priority": "Medium",
      "importance": "Urgent and Important",
      "confidence": 8
    }
  ]
}
Development Workflow
Branching Strategy (simple but professional)
main                 ← stable, deploy-ready code
feature/...          ← work on new features
fix/...              ← bug fixes
refactor/...         ← improvements without behavior changes
Typical workflow
git pull origin main
git switch -c feature/improve-prompt-engineering
# write code...
git add .
git commit -m "feat: improve date inference + example prompts"
git push -u origin feature/improve-prompt-engineering
# merge via GitHub
Roadmap
 Improve date inference (today/tomorrow/next week)
 Add user accounts + persistent tasks
 Build full frontend dashboard
 Add priority scoring system
 Deploy backend to Render/Fly.io and frontend to Netlify
 Mobile-friendly version

