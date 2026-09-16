const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000/api";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: options.body instanceof FormData ? options.headers : {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  const json = await res.json().catch(() => ({ success: false, error: { message: "Unexpected server response." } }));
  if (!res.ok || !json.success) {
    const message = json?.error?.message || `Request failed (${res.status})`;
    const err = new Error(message);
    err.status = res.status;
    err.code = json?.error?.code;
    throw err;
  }
  return json.data;
}

export const api = {
  health: () => request("/health"),

  uploadDocument: (file) => {
    const form = new FormData();
    form.append("file", file);
    return request("/documents/upload", { method: "POST", body: form });
  },
  loadDemo: () => request("/documents/demo", { method: "POST" }),
  listDocuments: () => request("/documents"),
  getDocument: (id) => request(`/documents/${id}`),
  getFullText: (id) => request(`/documents/${id}/text`),
  analyzeDocument: (id) => request(`/documents/${id}/analyze`, { method: "POST" }),
  getSummary: (id) => request(`/documents/${id}/summary`),
  getClauses: (id) => request(`/documents/${id}/clauses`),
  getRisks: (id) => request(`/documents/${id}/risks`),

  chat: (id, question, sessionId) =>
    request(`/documents/${id}/chat`, {
      method: "POST",
      body: JSON.stringify({ question, session_id: sessionId }),
    }),
  chatHistory: (id) => request(`/documents/${id}/chat/history`),
  legalInfo: (question) =>
    request("/legal-info", { method: "POST", body: JSON.stringify({ question }) }),

  compareByIds: (aId, bId) =>
    request("/compare", {
      method: "POST",
      body: JSON.stringify({ document_a_id: aId, document_b_id: bId }),
    }),
  compareByFiles: (fileA, fileB) => {
    const form = new FormData();
    form.append("document_a", fileA);
    form.append("document_b", fileB);
    return request("/compare", { method: "POST", body: form });
  },

  generateChecklist: (documentId) =>
    request("/checklist", { method: "POST", body: JSON.stringify({ document_id: documentId }) }),
  getChecklist: (documentId) => request(`/checklist/${documentId}`),
  toggleChecklistItem: (itemId, isDone) =>
    request(`/checklist/item/${itemId}`, { method: "PATCH", body: JSON.stringify({ is_done: isDone }) }),

  generateLawyerPrep: (documentId) =>
    request("/lawyer-prep", { method: "POST", body: JSON.stringify({ document_id: documentId }) }),
  getLawyerPrep: (documentId) => request(`/lawyer-prep/${documentId}`),

  // USP: Portfolio stats
  getStats: () => request("/stats"),

  // USP: Readability score
  getReadability: (id) => request(`/documents/${id}/readability`),

  // USP: Negotiation tips per clause
  getNegotiationTips: (docId, clauseId) =>
    request(`/documents/${docId}/clauses/${clauseId}/negotiate`, { method: "POST" }),

  // USP: Calendar export — returns a URL to trigger download
  getCalendarUrl: (id) => `${BASE_URL}/documents/${id}/calendar.ics`,
};
