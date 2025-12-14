// In Moodle, you'll read these from data-* attributes on the page.
const attemptId = 123; // placeholder
const slot = 1;
const apiBase = "http://localhost:8000/api/exam";

async function fetchQuestion() {
  const res = await fetch(`${apiBase}/question`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ attempt_id: attemptId, slot })
  });
  const data = await res.json();
  const root = document.getElementById("exam-root");
  if (root) {
    root.innerHTML = data.question_html;
  }
}

async function submitDummyAnswer() {
  const res = await fetch(`${apiBase}/answer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      attempt_id: attemptId,
      slot,
      response: { choice: "B" },
      client_timestamp: Date.now() / 1000
    })
  });
  console.log(await res.json());
}

fetchQuestion();
// submitDummyAnswer() can be wired to a button later.
