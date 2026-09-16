# LexiGuide AI

**Understand your legal documents. Know what matters.**

A GenAI-powered legal document intelligence platform that helps ordinary people
understand contracts, agreements, and policies — without requiring a law degree.

> LexiGuide AI provides informational assistance, not legal advice. For decisions
> involving your legal rights or obligations, consult a qualified legal professional.

---

## 🌟 Hackathon Upgrades (New Features)

This project has been massively overhauled to meet production-ready standards for your hackathon presentation. Recent upgrades include:

- **Exact Risk Highlighting (Problem Alignment):** Hovering over a risk now highlights the *exact* snippet of dangerous text in the document viewer, making it instantly clear to non-lawyers where the problem lies.
- **In-line Legal Glossary (Problem Alignment):** An intelligent jargon-detector that automatically spots complex terms (e.g., "indemnification", "severability") and provides a plain-English explanation on hover.
- **Enhanced Security:** Implemented `Flask-Limiter` for rate-limiting against abuse, added `Flask-Talisman` for HTTP security headers, and locked down CORS origins.
- **Optimized Efficiency:** Added SQL indexing for blazing-fast database queries, and implemented React Code Splitting (`React.lazy`) and Memoization (`React.memo`) for instant frontend loading.
- **Accessibility (a11y):** Full screen-reader support with `aria-live` and `aria-busy` tags for AI loading states, ensuring compliance and usability for all users.
- **Robust Testing:** Established a solid testing foundation with `pytest` for the backend and `vitest` + React Testing Library for the frontend.

## 🚀 Core Features

- **AI Document Analysis** — Plain-language summary, extracted parties, obligations, dates, and financial terms.
- **Plain-Language Explanations** — Every important clause explained in everyday language.
- **AI Risk Scanner** — Clause-level attention flags (High / Review Carefully / Standard), each with a suggested question for a lawyer.
- **Contract Comparison** — Upload two versions of a document and see what meaningfully changed.
- **Document Q&A (RAG)** — Ask questions about your document; answers are grounded in the actual text with cited source sections.
- **Action Checklist** — A concrete list of what to confirm before signing or acting.
- **Prepare for a Lawyer** — An auto-generated summary and question list for a real consultation.
- **Demo Mode** — A full pre-baked sample so you can explore every feature with **zero setup and no API key**.

---

## 💻 Quick Start (Hackathon Setup)

You can run the entire platform locally in just a few steps. 

### 1. Backend Setup (Flask)
Open a terminal and run the following commands:
```powershell
# Navigate to the backend directory
cd backend

# Create and activate a virtual environment (Windows)
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy the environment file and run the server
cp .env.example .env
python run.py
```
*(The backend will now be running on `http://127.0.0.1:5000`)*

### 2. Frontend Setup (React/Vite)
Open a **new** terminal and run:
```powershell
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```
*(The frontend will now be running on `http://localhost:5173`)*

---

## 🔑 Enabling Live AI Analysis (OpenRouter or Anthropic)

To analyze your own custom documents instead of just using Demo Mode, you need to add an API key.

1. Open `backend/.env`
2. Add your OpenRouter API key (or Anthropic API key):
   ```env
   LLM_API_KEY=sk-or-v1-...
   LLM_PROVIDER=openrouter
   LLM_MODEL=anthropic/claude-3.5-sonnet
   ```
3. **Important:** Restart the backend terminal (`CTRL+C` then `python run.py`) for the new key to take effect!

---

## 🏗️ Architecture

```text
Frontend (React + Tailwind + Vite)
        │
Backend API (Flask + Flask-Limiter + Flask-Talisman)
        │
Document Processing (PDF/DOCX/TXT extraction → chunking)
        │
RAG Retrieval (TF-IDF similarity search over chunks)
        │
LLM (OpenRouter / Anthropic via strict structured-JSON prompts)
        │
Structured Response → Frontend
```

Full technical detail can be found in [`docs/architecture.md`](docs/architecture.md) and the API reference in [`docs/api.md`](docs/api.md).

## 🗄️ Database

Runs on **SQLite by default** — zero setup, perfect for a hackathon demo. 
For production, `database/schema.sql` has the full **MySQL** schema; just point `DATABASE_URL` in `backend/.env` at your MySQL instance:

```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/lexiguide
```
All foreign keys are now fully indexed for maximum performance.

## 🔒 Security & Privacy

- Full document text is **not** stored in the database — only a short excerpt and derived structured data.
- The LLM API key stays server-side; the frontend never sees it.
- **XSS Protection:** React safely escapes all AI-generated output natively.
- **Rate Limiting:** `Flask-Limiter` protects all AI endpoints from abuse and DDoS attempts.
- **Security Headers:** `Flask-Talisman` enforces modern HTTP security policies.
