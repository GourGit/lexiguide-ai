import { useState } from "react";
import Navbar from "../components/Navbar";
import Disclaimer from "../components/Disclaimer";
import { api } from "../services/api";

const SUGGESTED = [
  "What is an NDA?",
  "What does indemnification mean?",
  "What is arbitration?",
  "What is a notice period?",
  "What is a non-compete clause?",
];

export default function LegalInfo() {
  const [question, setQuestion] = useState("");
  const [answers, setAnswers] = useState([]);
  const [loading, setLoading] = useState(false);

  async function ask(q) {
    const text = (q ?? question).trim();
    if (!text || loading) return;
    setQuestion("");
    setLoading(true);
    setAnswers((a) => [...a, { question: text, loading: true }]);
    try {
      const result = await api.legalInfo(text);
      setAnswers((a) => a.map((item, i) => (i === a.length - 1 ? { ...item, ...result, loading: false } : item)));
    } catch (err) {
      setAnswers((a) =>
        a.map((item, i) => (i === a.length - 1 ? { ...item, answer: `Error: ${err.message}`, loading: false } : item))
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="max-w-3xl mx-auto px-6 py-12">
        <h1 className="font-display text-3xl text-ink mb-2">Legal information</h1>
        <p className="text-ink-soft mb-8">
          Ask about general legal concepts. This is educational information, not personalized
          advice about your specific situation.
        </p>

        <div className="flex flex-wrap gap-2 mb-8">
          {SUGGESTED.map((q) => (
            <button
              key={q}
              onClick={() => ask(q)}
              className="text-xs border border-line rounded-full px-3 py-1.5 text-ink-soft hover:border-accent hover:text-accent transition-colors"
            >
              {q}
            </button>
          ))}
        </div>

        <div className="space-y-8 mb-8">
          {answers.map((a, i) => (
            <div key={i} className="rule pt-6">
              <p className="font-display text-lg text-ink mb-2">{a.question}</p>
              {a.loading ? (
                <p className="text-sm text-ink-soft">Thinking…</p>
              ) : (
                <>
                  <p className="text-sm text-ink leading-relaxed">{a.answer}</p>
                  {a.jurisdiction_note && (
                    <p className="text-xs text-attention mt-2">⚠ {a.jurisdiction_note}</p>
                  )}
                </>
              )}
            </div>
          ))}
        </div>

        <form onSubmit={(e) => { e.preventDefault(); ask(); }} className="flex gap-2">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask about a legal concept…"
            className="flex-1 border border-line rounded-md px-3 py-2 text-sm bg-white focus:outline-none focus:border-accent"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-accent text-white text-sm font-medium px-4 py-2 rounded-md hover:opacity-90 disabled:opacity-50"
          >
            Ask
          </button>
        </form>

        <Disclaimer />
      </main>
    </div>
  );
}
