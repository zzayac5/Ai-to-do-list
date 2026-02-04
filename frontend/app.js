const API_BASE_URL = "http://127.0.0.1:8000"; // this is just for local development
const CHAT_ENDPOINT = "/chat"; // adjust to actual endpoint where needed

const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const messagesDiv = document.getElementById("messages");
const rawResponsePre = document.getElementById("raw-response");
const tasksList = document.getElementById("tasks-list");

function addMessageToChat(role, text) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", role);

  const span = document.createElement("span");
  span.textContent = text;

  messageDiv.appendChild(span);
  messagesDiv.appendChild(messageDiv);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function sendMessage(messageText) {
  // Add user message to chat
  addMessageToChat("user", messageText);

  // Disable form while sending
  chatForm.querySelector("button").disabled = true;

  try {
    const response = await fetch(API_BASE_URL + CHAT_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message: messageText })
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();

    // Show assistant reply if present
    const replyText =
      data.reply ||
      data.assistant_reply ||
      "(No 'reply' field in response; showing raw JSON below.)";

    addMessageToChat("assistant", replyText);

    // Show raw JSON response
    rawResponsePre.textContent = JSON.stringify(data, null, 2);

    // Clear current tasks list
    tasksList.innerHTML = "";

    function renderTask(task, index) {
      const li = document.createElement("li");

      const id = task.id ? `#${task.id} ` : "";
      const title = task.title || task.description || `Task ${index + 1}`;
      const due = task.due_at || task.due_date || task.date || "";

      li.textContent = `${id}${title}${due ? " — due " + due : ""}`;
      tasksList.appendChild(li);
    }

    // Back-compat: if tasks array exists, render it.
    if (Array.isArray(data.tasks)) {
      data.tasks.forEach((task, index) => renderTask(task, index));
      return;
    }

    // New API: use tool_results to render created/listed/prioritized tasks.
    const collectedTasks = [];
    let prioritized = null;

    if (Array.isArray(data.tool_results)) {
      data.tool_results.forEach((tr) => {
        if (!tr || !tr.result) return;

        if (tr.name === "create_task" && typeof tr.result === "object" && !Array.isArray(tr.result)) {
          collectedTasks.push(tr.result);
        }

        if (tr.name === "list_tasks" && Array.isArray(tr.result)) {
          collectedTasks.push(...tr.result);
        }

        if (tr.name === "prioritize_tasks" && tr.result && Array.isArray(tr.result.results)) {
          prioritized = tr.result;
        }
      });
    }

    if (collectedTasks.length > 0) {
      collectedTasks.forEach((task, index) => renderTask(task, index));
      return;
    }

    if (prioritized) {
      prioritized.results.forEach((r, index) => {
        const li = document.createElement("li");
        const chance =
          typeof r.completion_chance === "number"
            ? ` chance=${Math.round(r.completion_chance * 100)}%`
            : "";
        li.textContent = `Task #${r.task_id} — priority=${r.priority_score.toFixed(2)}${chance}`;
        tasksList.appendChild(li);
      });
    }
  } catch (err) {
    console.error(err);
    addMessageToChat("assistant", "Error talking to backend: " + err.message);
    rawResponsePre.textContent = "Error: " + err.message;
  } finally {
    chatForm.querySelector("button").disabled = false;
  }
}

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = userInput.value.trim();
  if (!text) return;
  userInput.value = "";
  sendMessage(text);
});

let recognition;
let isRecording = false;

function setupVoiceInput() {
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    console.warn("Speech recognition not supported in this browser.");
    return;
  }

  recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = "en-US";

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    userInput.value = transcript;
    sendMessage(transcript);
  };

  recognition.onerror = (event) => {
    console.error("Speech recognition error:", event.error);
  };

  recognition.onend = () => {
    isRecording = false;
  };

  document.addEventListener("keydown", (e) => {
    if (e.key === "v" && !isRecording) {
      isRecording = true;
      recognition.start();
      console.log("Voice input started");
    }
  });
}

setupVoiceInput();
