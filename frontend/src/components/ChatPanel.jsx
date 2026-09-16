import { useState, useRef, useEffect } from "react";
import { api } from "../services/api";

const SUGGESTED = [
  "What am I agreeing to?",
  "What are my biggest obligations?",
  "What can I terminate?",
  "What could cost me money?",
  "What deadlines should I know?",
];

export default function ChatPanel({ documentId }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    if (!documentId) return;
    
    // Use an AbortController or a local flag to prevent race conditions
    let isActive = true;
    
    api.chatHistory(documentId)
      .then((history) => {
        if (isActive && history && history.length > 0) {
          setMessages(history);
        }
      })
      .catch(() => {})
      .finally(() => {
        if (isActive) {
          setHistoryLoaded(true);
        }
      });
      
    return () => {
      isActive = false;
    };
  }, [documentId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send(question) {
    const q = (question ?? input).trim();
    if (!q || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: q }]);
    setLoading(true);
    try {
      const data = await api.chat(documentId, q, sessionId);
      setSessionId(data.session_id);
      setMessages((m) => [...m, data.message]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `Something went wrong: ${err.message}`, answer_type: "error" },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto space-y-4 pr-1" aria-live="polite" aria-relevant="additions">
        {messages.length === 0 && (
          <div>
            <p className="text-sm text-ink-soft mb-3">Ask anything about this document.</p>
            <div className="flex flex-wrap gap-2">
              {SUGGESTED.map((q) => (
                <button
                  key={q}
                  onClick={() => send(q)}
                  className="text-xs border border-line rounded-full px-3 py-1.5 text-ink-soft hover:border-accent hover:text-accent transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[85%] rounded-lg px-4 py-3 text-sm leading-relaxed ${
                m.role === "user" ? "bg-accent text-white" : "bg-paper-dim text-ink"
              }`}
            >
              <p className="whitespace-pre-wrap">{m.content}</p>
              {m.role === "assistant" && m.source_label && (
                <p className="text-xs text-ink-soft mt-2">📄 Source: {m.source_label}</p>
              )}
              {m.role === "assistant" && m.confidence && (
                <p className="text-xs text-ink-soft mt-1 capitalize">
                  Confidence: {m.confidence}
                  {m.answer_type === "needs_professional_review" && " · Needs professional review"}
                </p>
              )}
            </div>
          </div>
        ))}
        {loading && <p className="text-xs text-ink-soft">Reading your document…</p>}
        <div ref={bottomRef} />
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send();
        }}
        className="flex gap-2 pt-4 mt-2 rule"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about this document…"
          className="flex-1 border border-line rounded-md px-3 py-2 text-sm bg-white focus:outline-none focus:border-accent"
        />
        <button
          type="submit"
          disabled={loading}
          aria-label="Send message"
          className="bg-accent text-white text-sm font-medium px-4 py-2 rounded-md hover:opacity-90 disabled:opacity-50"
        >
          Ask
        </button>
      </form>
    </div>
  );
}
