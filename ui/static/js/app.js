const form = document.getElementById("chat-form");
const input = document.getElementById("user-input");
const messages = document.getElementById("messages");
const chatId = document.getElementById("chat-id").value;

function addBubble(text, who) {
  const div = document.createElement("div");
  div.className = `bubble ${who}`;
  div.innerHTML = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const question = input.value.trim();
  if (!question) return;

  // USER bubble
  addBubble(question, "user");
  input.value = "";

  // TEMP bot bubble
  const loading = document.createElement("div");
  loading.className = "bubble bot";
  loading.innerHTML = "⏳ Tamizhi சிந்திக்கிறது...";
  messages.appendChild(loading);
  messages.scrollTop = messages.scrollHeight;

  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: question,
        chat_id: chatId
      })
    });

    const data = await res.json();
    loading.remove();

    if (data.answer) {
      addBubble(data.answer, "bot");
    } else {
      addBubble("⚠️ பதில் கிடைக்கவில்லை.", "bot");
    }

  } catch (err) {
    loading.remove();
    addBubble("⚠️ Server error. Try again.", "bot");
  }
});
