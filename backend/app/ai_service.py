"""
GenAI service layer. Every function here is a narrowly-scoped prompt
(per the hackathon-guide's hallucination-prevention section) rather than
one giant do-everything prompt. Each function:
  1. Builds a tightly scoped system + user prompt
  2. Requests structured JSON only
  3. Parses + validates the response before returning it
  4. Never lets the model invent facts not present in the supplied text
"""
import json
import re
from flask import current_app

try:
    import anthropic
except ImportError:  # pragma: no cover
    anthropic = None

try:
    import openai
except ImportError:  # pragma: no cover
    openai = None


class AIServiceError(Exception):
    pass


DISCLAIMER = (
    "LexiGuide AI provides informational assistance, not legal advice. "
    "For decisions involving your legal rights or obligations, consult a "
    "qualified legal professional."
)


def _extract_json(raw_text: str):
    """The model is asked to return pure JSON; this defensively strips any
    stray markdown fences before parsing."""
    cleaned = (raw_text or "").strip()
    cleaned = re.sub(r"^```(json)?|```$", "", cleaned, flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise AIServiceError(f"Model did not return valid JSON: {exc}") from exc


def _client():
    api_key = current_app.config.get("LLM_API_KEY")
    if not api_key:
        raise AIServiceError(
            "LLM_API_KEY is not configured. Add it to backend/.env to enable "
            "AI analysis, or use Demo Mode to explore the product with "
            "pre-generated sample results."
        )
    provider = current_app.config.get("LLM_PROVIDER", "anthropic")

    if provider == "openrouter":
        if openai is None:
            raise AIServiceError(
                "LLM_PROVIDER is set to 'openrouter' but the 'openai' package "
                "is not installed. Run: pip install openai"
            )
        base_url = current_app.config.get("LLM_BASE_URL") or "https://openrouter.ai/api/v1"
        return openai.OpenAI(api_key=api_key, base_url=base_url)

    if anthropic is None:
        raise AIServiceError("The 'anthropic' package is not installed.")
    return anthropic.Anthropic(api_key=api_key)


def _call(system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> dict:
    client = _client()
    provider = current_app.config.get("LLM_PROVIDER", "anthropic")
    model = current_app.config.get("LLM_MODEL", "claude-sonnet-4-6")

    try:
        if provider == "openrouter":
            # OpenRouter speaks the OpenAI-compatible chat completions format,
            # not Anthropic's native Messages API.
            response = client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            raw_text = response.choices[0].message.content
        else:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            raw_text = "\n".join(
                b.text for b in response.content if getattr(b, "type", "") == "text"
            )
    except Exception as exc:
        exc_str = str(exc)
        current_app.logger.error(f"LLM request failed: {exc_str}")
        
        if "402" in exc_str and "credits" in exc_str.lower():
            raise AIServiceError("Your AI API provider has run out of credits. Please add credits to your account or use Demo Mode.") from exc
        elif "429" in exc_str:
            raise AIServiceError("The AI service is currently busy or rate-limited. Please try again in a few moments.") from exc
        elif "401" in exc_str or "403" in exc_str:
            raise AIServiceError("Your AI API key is invalid or unauthorized. Please check your configuration.") from exc
        else:
            raise AIServiceError("The AI service encountered an unexpected error. Please try again later.") from exc

    return _extract_json(raw_text)


# ---------------------------------------------------------------------------
# FEATURE 1 + 4: Document analysis (summary, obligations, dates, financials)
# ---------------------------------------------------------------------------
ANALYSIS_SYSTEM_PROMPT = """You are LexiGuide AI, a legal document explainer for \
non-lawyers. You NEVER give definitive legal conclusions, NEVER state a \
clause is illegal, and ONLY use facts present in the supplied document text \
-- never invent parties, dates, or amounts. If something is not stated in \
the document, omit it or say it is not specified. Respond with ONLY a JSON \
object, no preamble, no markdown fences."""

ANALYSIS_USER_TEMPLATE = """Analyze the following legal document and return a JSON object \
with EXACTLY this shape:

{{
  "document_type": "short label, e.g. Employment Agreement",
  "parties": ["Party A description", "Party B description"],
  "executive_summary": "3-5 sentences in plain, everyday language",
  "key_points": ["short bullet", "short bullet", ...],
  "your_obligations": ["what the primary signer must do", ...],
  "other_party_obligations": ["what the other party must do", ...],
  "important_dates": [{{"label": "e.g. Notice period", "detail": "30 days before renewal"}}],
  "financial_terms": [{{"label": "e.g. Monthly rent", "amount": "as stated in the document"}}],
  "governing_law": "jurisdiction stated in the document, or null if not specified",
  "attention_score": 0-100 integer indicating how much of the document deserves careful review \
(this is NOT a legal risk probability, just a review-priority signal)
}}

Document text:
---
{document_text}
---
"""


def analyze_document(document_text: str) -> dict:
    prompt = ANALYSIS_USER_TEMPLATE.format(document_text=document_text[:18000])
    return _call(ANALYSIS_SYSTEM_PROMPT, prompt, max_tokens=2500)


# ---------------------------------------------------------------------------
# FEATURE 2 + 3: Clause extraction + plain-language explanation + risk scan
# ---------------------------------------------------------------------------
CLAUSES_SYSTEM_PROMPT = """You are LexiGuide AI's clause and risk scanner. For every \
notable clause you find, explain it in plain language and, where relevant, flag it for \
review. NEVER say a clause "is illegal" -- instead say it "may deserve careful review \
because...". Ground every finding in the literal text supplied. Respond with ONLY a JSON \
object, no preamble, no markdown fences."""

CLAUSES_USER_TEMPLATE = """From the document text below, identify important clauses \
(termination, liability, indemnification, confidentiality, IP, non-compete, non-solicitation, \
automatic renewal, arbitration, jurisdiction, data/privacy, penalties, dispute resolution -- \
only include types that actually appear). Return JSON:

{{
  "clauses": [
    {{
      "clause_type": "e.g. Termination",
      "original_text": "the relevant excerpt, verbatim from the document, under 60 words",
      "plain_explanation": "Simply put: ...",
      "why_it_matters": "practical significance for the user",
      "what_to_check": ["neutral question the user should consider", ...]
    }}
  ],
  "risk_findings": [
    {{
      "clause_snippet": "short excerpt, under 40 words",
      "risk_level": "high | medium | low | standard",
      "category": "e.g. Unlimited liability",
      "explanation": "why this may deserve attention, phrased neutrally",
      "why_it_matters": "practical consequence for the user",
      "suggested_question": "a specific question to ask a lawyer about this clause"
    }}
  ]
}}

risk_level guide: "high" = broad/unlimited obligations, one-sided termination, IP transfer, \
severe penalties. "medium" = automatic renewal, long notice periods, arbitration, jurisdiction \
away from the user. "low"/"standard" = ordinary, expected terms for this document type.

Document text:
---
{document_text}
---
"""


def extract_clauses_and_risks(document_text: str) -> dict:
    prompt = CLAUSES_USER_TEMPLATE.format(document_text=document_text[:18000])
    return _call(CLAUSES_SYSTEM_PROMPT, prompt, max_tokens=3000)


# ---------------------------------------------------------------------------
# FEATURE 5/6: Document-grounded Q&A (RAG) — answers ONLY from retrieved chunks
# ---------------------------------------------------------------------------
CHAT_SYSTEM_PROMPT = """You are LexiGuide AI answering a question about ONE specific \
uploaded document, using only the retrieved excerpts provided to you. If the excerpts do \
not contain the answer, you MUST respond that the information was not found -- never \
guess or use outside knowledge to fill the gap. Never present yourself as giving a legal \
conclusion. Respond with ONLY a JSON object, no preamble, no markdown fences."""

CHAT_USER_TEMPLATE = """The user asked a question about their uploaded document. You are \
given the most relevant retrieved excerpts (this is NOT the full document). Answer using \
ONLY these excerpts.

Question: {question}

Retrieved excerpts:
{excerpts}

Return JSON:
{{
  "found_in_document": true/false,
  "answer": "the answer in plain language, or an explanation that it could not be found",
  "source_section": "the section_label of the excerpt that supports the answer, or null",
  "confidence": "high | medium | low",
  "answer_type": "document_based | needs_professional_review"
}}

If found_in_document is false, set answer to something like: "I couldn't find this \
information in the uploaded document." and confidence to "low".
"""


def answer_from_document(question: str, retrieved_chunks: list) -> dict:
    excerpts = "\n\n".join(
        f"[{c.get('section_label', 'Section')}] {c['content']}" for c in retrieved_chunks
    ) or "(no relevant excerpts retrieved)"
    prompt = CHAT_USER_TEMPLATE.format(question=question, excerpts=excerpts[:12000])
    return _call(CHAT_SYSTEM_PROMPT, prompt, max_tokens=1200)


# ---------------------------------------------------------------------------
# FEATURE 9: General legal information mode (NOT document-specific)
# ---------------------------------------------------------------------------
LEGAL_INFO_SYSTEM_PROMPT = """You are LexiGuide AI's general legal information mode. \
Explain legal concepts in plain language for a non-lawyer. This is general education, \
never personalized advice about the user's own situation. If the answer depends on \
jurisdiction, say so explicitly and ask the user to specify their country/state. Respond \
with ONLY a JSON object, no preamble, no markdown fences."""

LEGAL_INFO_USER_TEMPLATE = """Question: {question}

Return JSON:
{{
  "answer": "plain-language explanation",
  "jurisdiction_note": "note if this varies by jurisdiction, or null if universal",
  "answer_type": "general_legal_information"
}}
"""


def answer_general_legal_question(question: str) -> dict:
    prompt = LEGAL_INFO_USER_TEMPLATE.format(question=question)
    return _call(LEGAL_INFO_SYSTEM_PROMPT, prompt, max_tokens=800)


# ---------------------------------------------------------------------------
# FEATURE 4: Contract comparison
# ---------------------------------------------------------------------------
COMPARE_SYSTEM_PROMPT = """You are LexiGuide AI comparing two versions of a legal document. \
Identify meaningful differences only -- ignore formatting/whitespace noise. Ground every \
item in the literal text of both documents. Respond with ONLY a JSON object, no preamble, \
no markdown fences."""

COMPARE_USER_TEMPLATE = """Compare Document A and Document B below.

Document A:
---
{doc_a}
---

Document B:
---
{doc_b}
---

Return JSON:
{{
  "added": ["clause or term present in B but not A", ...],
  "removed": ["clause or term present in A but not B", ...],
  "modified": [{{"aspect": "e.g. Payment", "before": "as in A", "after": "as in B"}}],
  "plain_summary": "a concise, plain-language paragraph explaining what meaningfully changed \
and why it matters"
}}
"""


def compare_documents(doc_a_text: str, doc_b_text: str) -> dict:
    prompt = COMPARE_USER_TEMPLATE.format(doc_a=doc_a_text[:9000], doc_b=doc_b_text[:9000])
    return _call(COMPARE_SYSTEM_PROMPT, prompt, max_tokens=2000)


# ---------------------------------------------------------------------------
# FEATURE 7: Action checklist
# ---------------------------------------------------------------------------
CHECKLIST_SYSTEM_PROMPT = """You generate short, actionable checklists for someone about to \
sign or act on a legal document, based only on clauses/risks actually found in it. Respond \
with ONLY a JSON object, no preamble, no markdown fences."""

CHECKLIST_USER_TEMPLATE = """Based on this analysis of a legal document, generate a checklist.

Key points: {key_points}
Risk findings: {risk_findings}

Return JSON:
{{
  "checklist": [
    {{"text": "short action item, e.g. Confirm termination notice period", \
"explanation": "one short sentence on why"}}
  ]
}}
Generate 4-8 items, prioritizing the highest-attention items first.
"""


def generate_checklist(key_points: list, risk_findings: list) -> dict:
    prompt = CHECKLIST_USER_TEMPLATE.format(
        key_points=json.dumps(key_points), risk_findings=json.dumps(risk_findings)
    )
    return _call(CHECKLIST_SYSTEM_PROMPT, prompt, max_tokens=1200)


# ---------------------------------------------------------------------------
# FEATURE 8: Prepare for a lawyer
# ---------------------------------------------------------------------------
LAWYER_PREP_SYSTEM_PROMPT = """You help a non-lawyer prepare for a consultation with a \
real lawyer about a specific document. You are not giving legal advice yourself -- you are \
helping the user communicate clearly and ask good questions. Respond with ONLY a JSON \
object, no preamble, no markdown fences."""

LAWYER_PREP_USER_TEMPLATE = """Based on this document analysis, prepare consultation materials.

Document type: {document_type}
Executive summary: {summary}
Risk findings: {risk_findings}

Return JSON:
{{
  "summary_for_lawyer": "a concise 3-5 sentence summary of the document and likely areas of \
concern, written for a lawyer to quickly get oriented",
  "questions": ["specific, well-formed question to ask the lawyer", ...],
  "documents_to_bring": ["e.g. Signed copy of the agreement", "Any prior correspondence", ...]
}}
Generate 4-8 questions, each tied to a specific clause or risk found in this document.
"""


def generate_lawyer_prep(document_type: str, summary: str, risk_findings: list) -> dict:
    prompt = LAWYER_PREP_USER_TEMPLATE.format(
        document_type=document_type or "Legal document",
        summary=summary or "",
        risk_findings=json.dumps(risk_findings),
    )
    return _call(LAWYER_PREP_SYSTEM_PROMPT, prompt, max_tokens=1500)


# ---------------------------------------------------------------------------
# USP: Negotiation tips per clause
# ---------------------------------------------------------------------------
NEGOTIATE_SYSTEM_PROMPT = """You are LexiGuide AI's negotiation coach. For a specific legal \
clause, you suggest 1-3 concrete, plain-language negotiation angles that the user could \
raise with the other party. You are NOT giving legal advice — you are helping the user \
understand what aspects of this clause are commonly negotiable and what questions to raise. \
Never say a clause "is illegal". Ground every tip in the actual clause text provided. \
Respond with ONLY a JSON object, no preamble, no markdown fences."""

NEGOTIATE_USER_TEMPLATE = """Clause type: {clause_type}

Original clause text:
\"\"\"{original_text}\"\"\"

Plain explanation: {plain_explanation}

Suggest 1-3 specific, practical negotiation angles for this clause. Each tip should be \
actionable and in plain language a non-lawyer can understand and use in a conversation.

Return JSON:
{{
  "tips": [
    {{
      "title": "short label, e.g. Shorten the notice period",
      "suggestion": "What you could ask for and why it is reasonable, in 1-2 sentences.",
      "example_phrasing": "An example sentence the user could say or write to raise this point."
    }}
  ]
}}
Generate 1-3 tips. Only include tips that are genuinely relevant to this specific clause.
"""


def generate_negotiation_tips(clause_type: str, original_text: str, plain_explanation: str) -> dict:
    prompt = NEGOTIATE_USER_TEMPLATE.format(
        clause_type=clause_type or "Clause",
        original_text=(original_text or "")[:2000],
        plain_explanation=plain_explanation or "",
    )
    return _call(NEGOTIATE_SYSTEM_PROMPT, prompt, max_tokens=900)