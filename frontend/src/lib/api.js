// Central API layer. In dev, REACT_APP_BACKEND_URL is empty and the CRA proxy
// (package.json "proxy") forwards /api to the backend. In production, set
// REACT_APP_BACKEND_URL to the deployed backend origin.
const BASE = (process.env.REACT_APP_BACKEND_URL || "").replace(/\/$/, "");

const url = (path) => `${BASE}${path}`;

export async function listDocuments() {
  const res = await fetch(url("/api/documents"));
  if (!res.ok) throw new Error("Failed to load documents");
  return res.json();
}

export async function uploadDocument(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(url("/api/documents/upload"), { method: "POST", body: form });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Upload failed");
  return data;
}

export async function deleteDocument(docId) {
  const res = await fetch(url(`/api/documents/${docId}`), { method: "DELETE" });
  if (!res.ok) throw new Error("Delete failed");
  return res.json();
}

export async function fetchHistory(sessionId) {
  const res = await fetch(url(`/api/chat/history/${sessionId}`));
  if (!res.ok) return [];
  return res.json();
}

export async function clearHistory(sessionId) {
  const res = await fetch(url(`/api/chat/history/${sessionId}`), { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to clear history");
  return res.json();
}

/**
 * Stream a chat answer. Calls handlers as Server-Sent Events arrive:
 *   onSources(string[]), onToken(string), onError(string), onDone()
 */
export async function streamChat({ query, sessionId, onSources, onToken, onError, onDone }) {
  const res = await fetch(url("/api/chat"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, session_id: sessionId }),
  });

  if (!res.ok || !res.body) {
    const data = await res.json().catch(() => ({}));
    onError?.(data.detail || "The server could not process your request.");
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const parts = buffer.split("\n\n");
    buffer = parts.pop() || "";

    for (const part of parts) {
      const line = part.trim();
      if (!line.startsWith("data:")) continue;
      let evt;
      try {
        evt = JSON.parse(line.slice(5).trim());
      } catch {
        continue;
      }
      if (evt.type === "sources") onSources?.(evt.sources || []);
      else if (evt.type === "token") onToken?.(evt.content || "");
      else if (evt.type === "error") onError?.(evt.message || "An error occurred.");
      else if (evt.type === "done") onDone?.();
    }
  }
}
