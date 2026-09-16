# Architecture

## Pipeline

```
Frontend (React)
     │  fetch()
     ▼
Backend API (Flask, REST, JSON)
     │
     ▼
Document Processing
  ├─ Text Extraction   (pypdf / python-docx / plain read)
  └─ Chunking          (paragraph/heading-aware, ~900 chars, small overlap)
     │
     ▼
RAG Retrieval
  ├─ TF-IDF vectorization of chunks (scikit-learn)
  └─ Cosine similarity search against the user's question
     │
     ▼
LLM (Claude API)
  ├─ Narrowly-scoped prompt per feature (analysis, clauses/risk,
  │   chat, compare, checklist, lawyer-prep, legal-info)
  ├─ System prompt enforces: no invented facts, no "illegal" verdicts,
  │   cite source section, say "not found" rather than guess
  └─ Structured JSON output only, parsed + validated before use
     │
     ▼
Structured Response → Frontend
  (summary, clauses, risk findings, chat answer + source + confidence,
   comparison diff, checklist, lawyer-prep package)
```

## Why each design choice

**Narrow prompts over one mega-prompt.** Each GenAI feature (`app/ai_service.py`) is
its own function with its own system + user prompt, scoped to exactly one task. This
is the single biggest lever against hallucination — a model asked to "analyze this
whole document and also assess risk and also compare and also answer questions" in
one shot degrades quality across all of them. Scoping also makes each feature testable
in isolation and lets the JSON schema be enforced tightly per feature.

**RAG for chat, full-text for analysis.** Whole-document analysis (summary, clauses,
risk scan) intentionally sends the (truncated) full text, because those features need
document-wide context. Chat, by contrast, retrieves only the top-k most relevant chunks
per question — this keeps answers grounded to specific passages (enabling source
citation) and avoids re-sending the entire document on every message.

**TF-IDF instead of a downloaded embedding model.** The retrieval step needs *a*
similarity search over chunks, but not necessarily a neural embedding model — TF-IDF +
cosine similarity is simple, deterministic, needs no external model download, and is
"good enough" for legal documents where clause-specific vocabulary (e.g. "indemnify",
"arbitration", "notice period") is exactly the kind of signal TF-IDF captures well.
`app/rag.py` isolates this behind a small interface so it can be swapped for a hosted
embedding provider + vector DB without touching the rest of the app.

**Full document text lives on disk, not in the database.** Per the "don't store
sensitive content unnecessarily" principle, only a short excerpt and the AI-derived
structured data (summary, clauses, risk findings) are persisted in SQL. The full text
is used transiently for analysis/chat and kept in local file storage, not in the
long-lived structured tables that back the dashboard and history views.

**Structured JSON responses everywhere.** Every LLM call requests a specific JSON
shape and the backend validates/parses it before touching the database or the API
response. This keeps the frontend rendering predictable and makes it easy to add new
UI (e.g. a new dashboard widget) without changing the prompt.

**Graceful degradation without an API key.** Every AI-dependent route catches a
missing/invalid key and returns a clear, user-facing message rather than a stack
trace. Document chat specifically falls back to returning the best-matching retrieved
excerpt (clearly labeled) so the RAG pipeline is still demonstrable without a live key;
full analysis/compare/checklist/lawyer-prep point the user to Demo Mode instead.

## Data model

See `backend/app/models.py` (SQLAlchemy, database-agnostic) and `database/schema.sql`
(MySQL DDL for production) — both define the same eleven tables: `users`, `documents`,
`document_chunks`, `analyses`, `clauses`, `risk_findings`, `chat_sessions`,
`chat_messages`, `checklists`, `document_comparisons`, `lawyer_questions`.
