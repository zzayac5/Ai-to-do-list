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

    // If tasks array exists, render it
    if (Array.isArray(data.tasks)) {
      data.tasks.forEach((task, index) => {
        const li = document.createElement("li");

        // Try to be defensive about fields
        const description = task.description || task.title || `Task ${index + 1}`;
        const date = task.date || task.due_date || task.dueTime || "";
        const time = task.time || task.start_time || "";

        li.textContent = `${description}${
          date || time ? " — " + [date, time].filter(Boolean).join(" @ ") : ""
        }`;

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
