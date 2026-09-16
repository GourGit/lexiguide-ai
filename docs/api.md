# API Reference

Base URL: `http://localhost:5000/api`

All responses are JSON: `{"success": true, "data": ...}` or
`{"success": false, "error": {"message": "...", "code": "..."}}`.

## Health

`GET /health` → `{ status, database, llm_configured }`

## Documents

| Method | Path | Description |
|---|---|---|
| POST | `/documents/upload` | Multipart `file` (PDF/DOCX/TXT, ≤15MB) → creates a document, extracts + chunks text |
| GET | `/documents` | List all documents |
| GET | `/documents/:id` | Get one document |
| GET | `/documents/:id/text` | Full extracted text (for the document viewer) |
| POST | `/documents/:id/analyze` | Runs AI analysis + clause/risk extraction, persists results |
| GET | `/documents/:id/summary` | Structured analysis (summary, obligations, dates, financial terms, attention score) |
| GET | `/documents/:id/clauses` | Extracted clauses with plain-language explanations |
| GET | `/documents/:id/risks` | Risk findings (level, category, explanation, suggested question) |
| POST | `/documents/demo` | Loads (or reuses) the pre-baked demo Employment Agreement — works with no API key |

## Chat (RAG document Q&A)

| Method | Path | Description |
|---|---|---|
| POST | `/documents/:id/chat` | Body: `{question, session_id?}` → retrieves relevant chunks, answers grounded in the document with source + confidence |
| GET | `/documents/:id/chat/history` | Most recent chat session's messages |

## Legal information mode (general, not document-specific)

| Method | Path | Description |
|---|---|---|
| POST | `/legal-info` | Body: `{question}` → plain-language explanation of a legal concept, with a jurisdiction note if relevant |

## Comparison

| Method | Path | Description |
|---|---|---|
| POST | `/compare` | Multipart `document_a` + `document_b` **or** JSON `{document_a_id, document_b_id}` → added/removed/modified terms + plain-language summary |

## Checklist

| Method | Path | Description |
|---|---|---|
| POST | `/checklist` | Body: `{document_id}` → generates (or returns existing) checklist items |
| GET | `/checklist/:document_id` | List checklist items |
| PATCH | `/checklist/item/:item_id` | Body: `{is_done}` → toggle completion |

## Lawyer preparation

| Method | Path | Description |
|---|---|---|
| POST | `/lawyer-prep` | Body: `{document_id}` → summary for lawyer, questions to ask, documents to bring |
| GET | `/lawyer-prep/:document_id` | Fetch existing lawyer-prep package |

## Error codes

- `EXTRACTION_FAILED` (422) — unreadable file (e.g. scanned image with no text layer)
- `AI_SERVICE_ERROR` (502) — LLM call failed or `LLM_API_KEY` not configured
- `409` — action requires analysis to run first
- `410` — original document text no longer available on disk
- `413` — file exceeds size limit
- `415` — unsupported file type
