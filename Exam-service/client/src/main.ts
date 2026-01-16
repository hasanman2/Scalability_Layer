// client/src/main.ts

interface QuestionPayload {
  attempt_id: number;
  slot: number;
  question_html: string;
  meta?: Record<string, unknown>;
}

interface AnswerResponse {
  status: string;
}

function initExamClient() {
  const root = document.getElementById("exam-root") as HTMLDivElement | null;

  if (!root) {
    console.error("Exam client: #exam-root not found on page.");
    return;
  }

  const attemptIdAttr = root.dataset.attemptId;
  const slotAttr = root.dataset.slot;
  const apiBaseAttr = root.dataset.apiBase;

  if (!attemptIdAttr) {
    console.error("Exam client: data-attempt-id missing on #exam-root.");
    return;
  }

  const attemptId = Number(attemptIdAttr);
  const slot = Number(slotAttr ?? "1");
  const apiBase = apiBaseAttr ?? "http://localhost:8000/api/exam";

  if (Number.isNaN(attemptId) || Number.isNaN(slot)) {
    console.error("Exam client: attempt_id or slot is not a valid number.", {
      attemptIdAttr,
      slotAttr,
    });
    return;
  }

  async function fetchQuestion() {
    try {
      const res = await fetch(`${apiBase}/question`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          attempt_id: attemptId,
          slot: slot,
        }),
      });

      if (!res.ok) {
        console.error("Exam client: /question returned error", res.status);
        return;
      }

      const data = (await res.json()) as QuestionPayload;

      // Render HTML from the Exam Service (which ultimately comes from Moodle)
      root.innerHTML = data.question_html;

      //attach a simple debug button for submitting a dummy answer
      const debugBtn = document.createElement("button");
      debugBtn.textContent = "Submit dummy answer";
      debugBtn.type = "button";
      debugBtn.onclick = submitDummyAnswer;
      root.appendChild(debugBtn);
    } catch (err) {
      console.error("Exam client: failed to fetch question", err);
    }
  }

  async function submitDummyAnswer() {
  try {
    const res = await fetch(`${apiBase}/answer`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        attempt_id: attemptId,
        slot: slot,
        response: {
          text: "dummy student answer",
        },
        client_timestamp: Date.now() / 1000,
      }),
    });

    if (!res.ok) {
      console.error("Exam client: /answer returned error", res.status);
      return;
    }

    const data = (await res.json()) as AnswerResponse;
    console.log("Exam client: answer submission result", data);
  } catch (err) {
    console.error("Exam client: failed to submit answer", err);
  }
}


  // Initial question load
  fetchQuestion();
}

// Run as soon as DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initExamClient);
} else {
  initExamClient();
}
