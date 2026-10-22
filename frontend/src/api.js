const API_BASE = "http://127.0.0.1:8000";

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  return res.json();
}

export async function askTutor(question) {
  const res = await fetch(`${API_BASE}/search?question=${encodeURIComponent(question)}`);
  if (!res.ok) throw new Error("Failed to query engineering tutor");
  return res.json();
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export async function listDocuments() {
  const res = await fetch(`${API_BASE}/documents`);
  return res.json();
}

export async function ingestSampleDocuments() {
  const res = await fetch(`${API_BASE}/ingest-samples`, { method: "POST" });
  return res.json();
}

export async function generateQuiz(topic = null, numQuestions = 3, studentId = "student_1") {
  const res = await fetch(`${API_BASE}/quiz/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, num_questions: numQuestions, student_id: studentId }),
  });
  if (!res.ok) throw new Error("Failed to generate quiz");
  return res.json();
}

export async function submitQuiz(quizId, answers, studentId = "student_1") {
  const res = await fetch(`${API_BASE}/quiz/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ quiz_id: quizId, answers, student_id: studentId }),
  });
  if (!res.ok) throw new Error("Failed to submit quiz");
  return res.json();
}

export async function getLearningProgress(studentId = "student_1") {
  const res = await fetch(`${API_BASE}/adaptive/progress?student_id=${studentId}`);
  return res.json();
}

export async function getTopicRecommendation(studentId = "student_1") {
  const res = await fetch(`${API_BASE}/adaptive/recommend?student_id=${studentId}`);
  return res.json();
}

export async function createStudyPlan(goal, hoursAvailable = 6.0, studentId = "student_1") {
  const res = await fetch(`${API_BASE}/adaptive/study-plan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ goal, hours_available: hoursAvailable, student_id: studentId }),
  });
  if (!res.ok) throw new Error("Failed to create study plan");
  return res.json();
}

export async function getStudyPlan(studentId = "student_1") {
  const res = await fetch(`${API_BASE}/adaptive/study-plan?student_id=${studentId}`);
  return res.json();
}

export async function sendAgentMessage(message, studentId = "student_1") {
  const res = await fetch(`${API_BASE}/agent/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, student_id: studentId }),
  });
  if (!res.ok) throw new Error("Agent cycle failed");
  return res.json();
}

export async function listMCPTools() {
  const res = await fetch(`${API_BASE}/mcp/tools`);
  return res.json();
}

export async function invokeMCPTool(toolName, args = {}) {
  const res = await fetch(`${API_BASE}/mcp/call`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: toolName, arguments: args }),
  });
  return res.json();
}

export async function simulateVoice(transcript, studentId = "student_1") {
  const res = await fetch(`${API_BASE}/voice/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ transcript, student_id: studentId }),
  });
  if (!res.ok) throw new Error("Voice simulation failed");
  return res.json();
}
