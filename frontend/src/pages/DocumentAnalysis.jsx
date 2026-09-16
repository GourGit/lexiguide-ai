import { useEffect, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import Navbar from "../components/Navbar";
import Disclaimer from "../components/Disclaimer";
import AttentionScore from "../components/AttentionScore";
import Timeline from "../components/Timeline";
import ClauseCard from "../components/ClauseCard";
import RiskCard from "../components/RiskCard";
import ChatPanel from "../components/ChatPanel";
import ChecklistItemRow from "../components/ChecklistItemRow";
import ReadabilityMeter from "../components/ReadabilityMeter";
import GlossaryText from "../components/GlossaryText";
import { api } from "../services/api";

const TABS = ["Overview", "Clauses", "Risks", "Obligations", "Timeline", "Ask AI"];

export default function DocumentAnalysis() {
  const { id } = useParams();
  const [document, setDocument] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [clauses, setClauses] = useState([]);
  const [risks, setRisks] = useState([]);
  const [checklist, setChecklist] = useState([]);
  const [lawyerPrep, setLawyerPrep] = useState(null);
  const [fullText, setFullText] = useState("");
  const [tab, setTab] = useState("Overview");
  const [highlightText, setHighlightText] = useState(null);
  const [searchQuery, setSearchQuery] = useState(""); // USP 6: document text search
  const [readability, setReadability] = useState(null); // USP 2: readability score
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => { 
    // load() handles loading state correctly and prevents race conditions
    // oxlint warns about calling it directly, but since load() is an async function
    // that wraps state updates, the best way to handle this in React is using an AbortController.
    // However, to keep it simple and satisfy the linter, we can just ensure state is handled safely.
    let isActive = true;
    
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const doc = await api.getDocument(id);
        if (!isActive) return;
        setDocument(doc);
        const [a, c, r, text] = await Promise.all([
          api.getSummary(id).catch(() => null),
          api.getClauses(id).catch(() => []),
          api.getRisks(id).catch(() => []),
          api.getFullText(id).catch(() => ({ text: "" })),
        ]);
        if (!isActive) return;
        setAnalysis(a);
        setClauses(c);
        setRisks(r);
        setFullText(text.text);
        
        // Non-blocking fetches
        api.getChecklist(id).then(res => isActive && setChecklist(res)).catch(() => {});
        api.getLawyerPrep(id).then(res => isActive && setLawyerPrep(res)).catch(() => {});
        api.getReadability(id).then(res => isActive && setReadability(res)).catch(() => {});
      } catch (err) {
        if (isActive) setError(err.message);
      } finally {
        if (isActive) setLoading(false);
      }
    };
    
    fetchData();
    
    return () => {
      isActive = false;
    };
  }, [id]);

  async function generateChecklist() {
    const items = await api.generateChecklist(id);
    setChecklist(items);
  }

  async function generateLawyerPrepNow() {
    const prep = await api.generateLawyerPrep(id);
    setLawyerPrep(prep);
  }

  async function toggleItem(item) {
    const updated = await api.toggleChecklistItem(item.id, !item.is_done);
    setChecklist((items) => items.map((i) => (i.id === item.id ? updated : i)));
  }

  // USP 5: Calendar export
  function downloadCalendar() {
    const url = api.getCalendarUrl(id);
    const a = window.document.createElement("a");
    a.href = url;
    a.download = `${document?.filename?.replace(/\.[^.]+$/, "") || "document"}-deadlines.ics`;
    a.click();
  }

  // USP 1: Print report — renders a hidden print-formatted div and triggers window.print()
  function printReport() {
    window.print();
  }

  if (loading) return <Shell><div aria-live="polite" aria-busy="true"><p className="text-sm text-ink-soft">Loading document…</p></div></Shell>;
  if (error) return <Shell><p className="text-sm text-high">{error}</p></Shell>;

  // USP 6: compute highlighted lines based on searchQuery OR highlightText
  const activeQuery = searchQuery.trim().toLowerCase();

  return (
    <>
      {/* USP 1: Hidden print report section — only visible during window.print() */}
      <div className="print-only print-report" aria-hidden="true">
        <h1 style={{ fontSize: "20px", fontWeight: "bold", marginBottom: "4px" }}>
          LexiGuide AI — Analysis Report
        </h1>
        <p style={{ color: "#64748b", fontSize: "12px", marginBottom: "16px" }}>
          {document?.filename} · Generated {new Date().toLocaleDateString()}
        </p>
        {analysis && (
          <>
            <h2 style={{ fontSize: "15px", fontWeight: "600", marginBottom: "6px" }}>Executive Summary</h2>
            <p style={{ fontSize: "12px", marginBottom: "12px" }}>{analysis.executive_summary}</p>

            <h2 style={{ fontSize: "15px", fontWeight: "600", marginBottom: "6px" }}>Key Points</h2>
            <ul style={{ fontSize: "12px", paddingLeft: "16px", marginBottom: "12px" }}>
              {analysis.key_points?.map((k, i) => <li key={i}>{k}</li>)}
            </ul>

            {risks.length > 0 && (
              <>
                <h2 style={{ fontSize: "15px", fontWeight: "600", marginBottom: "6px" }}>Risk Findings</h2>
                {risks.map((r, i) => (
                  <div key={i} style={{ marginBottom: "8px" }}>
                    <strong style={{ fontSize: "12px" }}>[{r.risk_level?.toUpperCase()}] {r.category}</strong>
                    <p style={{ fontSize: "11px", color: "#475569" }}>{r.explanation}</p>
                  </div>
                ))}
              </>
            )}

            {analysis.your_obligations?.length > 0 && (
              <>
                <h2 style={{ fontSize: "15px", fontWeight: "600", marginBottom: "6px" }}>Your Obligations</h2>
                <ul style={{ fontSize: "12px", paddingLeft: "16px", marginBottom: "12px" }}>
                  {analysis.your_obligations.map((o, i) => <li key={i}>{o}</li>)}
                </ul>
              </>
            )}

            {analysis.important_dates?.length > 0 && (
              <>
                <h2 style={{ fontSize: "15px", fontWeight: "600", marginBottom: "6px" }}>Important Dates</h2>
                <ul style={{ fontSize: "12px", paddingLeft: "16px", marginBottom: "12px" }}>
                  {analysis.important_dates.map((d, i) => (
                    <li key={i}><strong>{d.label}</strong>: {d.detail}</li>
                  ))}
                </ul>
              </>
            )}

            {checklist.length > 0 && (
              <>
                <h2 style={{ fontSize: "15px", fontWeight: "600", marginBottom: "6px" }}>Action Checklist</h2>
                <ul style={{ fontSize: "12px", paddingLeft: "16px", marginBottom: "12px" }}>
                  {checklist.map((c, i) => <li key={i}>{c.text}</li>)}
                </ul>
              </>
            )}

            <p style={{ fontSize: "10px", color: "#94a3b8", marginTop: "16px", borderTop: "1px solid #e2e8f0", paddingTop: "8px" }}>
              LexiGuide AI provides informational assistance only, not legal advice. Consult a qualified legal professional for decisions involving your legal rights or obligations.
            </p>
          </>
        )}
      </div>

      <div className="min-h-screen no-print">
        <Navbar />
        <div className="border-b border-line px-6">
          <div className="max-w-6xl mx-auto flex gap-1 overflow-x-auto">
            {TABS.map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={`px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                  tab === t ? "border-accent text-ink" : "border-transparent text-ink-soft hover:text-ink"
                }`}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        <main className="max-w-6xl mx-auto px-6 py-8 grid lg:grid-cols-5 gap-10">
          {/* LEFT: document viewer with USP 6 search */}
          <aside className="lg:col-span-2 order-2 lg:order-1">
            <div className="flex items-center gap-2 mb-2">
              <p className="text-xs uppercase tracking-wide text-ink-soft flex-1 truncate">
                {document.filename}
              </p>
            </div>
            {/* USP 6: Search input */}
            <div className="relative mb-2">
              <input
                type="search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search in document…"
                className="w-full border border-line rounded-md px-3 py-1.5 text-xs bg-white focus:outline-none focus:border-accent pr-8"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-ink-soft hover:text-ink text-sm"
                  aria-label="Clear search"
                >
                  ✕
                </button>
              )}
            </div>
            <div className="border border-line rounded-lg p-5 max-h-[70vh] overflow-y-auto bg-white">
              <pre className="whitespace-pre-wrap font-sans text-sm text-ink leading-relaxed">
                {fullText.split("\n").map((line, i) => {
                  const lineL = line.toLowerCase();
                  const matchesSearch = activeQuery && lineL.includes(activeQuery);
                  const matchesText =
                    !activeQuery &&
                    highlightText &&
                    lineL.includes(highlightText.toLowerCase());
                  return (
                    <span
                      key={i}
                      className={
                        matchesSearch
                          ? "bg-yellow-200 block"
                          : matchesText
                          ? "bg-attention-soft block"
                          : "block"
                      }
                    >
                      {line || "\u00A0"}
                    </span>
                  );
                })}
              </pre>
            </div>
          </aside>

          {/* RIGHT: AI analysis panel */}
          <section className="lg:col-span-3 order-1 lg:order-2">
            {tab === "Overview" && analysis && (
              <div className="space-y-8">
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="font-display text-2xl text-ink mb-1">{document.document_type}</h2>
                    <p className="text-xs text-ink-soft">
                      {analysis.parties?.join("  ·  ")}
                    </p>
                  </div>
                  {/* USP 1: Export Report button */}
                  <button
                    onClick={printReport}
                    title="Export analysis as PDF"
                    className="text-xs font-medium text-ink-soft border border-line rounded-md px-3 py-1.5 hover:border-accent hover:text-accent transition-colors"
                  >
                    📄 Export report
                  </button>
                </div>
                <AttentionScore score={analysis.attention_score} risks={risks} />
                {/* USP 2: Readability meter */}
                <ReadabilityMeter data={readability} />
                <div>
                  <h3 className="font-display text-lg text-ink mb-2">Executive summary</h3>
                  <p className="text-sm text-ink leading-relaxed"><GlossaryText text={analysis.executive_summary} /></p>
                </div>
                <div>
                  <h3 className="font-display text-lg text-ink mb-2">Key points</h3>
                  <ul className="text-sm text-ink space-y-1.5 list-disc list-inside">
                    {analysis.key_points?.map((k, i) => <li key={i}>{k}</li>)}
                  </ul>
                </div>
                {analysis.financial_terms?.length > 0 && (
                  <div>
                    <h3 className="font-display text-lg text-ink mb-2">Financial terms</h3>
                    <ul className="space-y-1.5">
                      {analysis.financial_terms.map((f, i) => (
                        <li key={i} className="flex justify-between text-sm border-b border-line py-1.5">
                          <span className="text-ink-soft">{f.label}</span>
                          <span className="text-ink font-medium">{f.amount}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                {analysis.governing_law && (
                  <div>
                    <h3 className="font-display text-lg text-ink mb-2">Governing law</h3>
                    <p className="text-sm text-ink">{analysis.governing_law}</p>
                  </div>
                )}
              </div>
            )}

            {tab === "Clauses" && (
              <div>
                <h2 className="font-display text-2xl text-ink mb-4">Important clauses</h2>
                {clauses.length === 0 && <p className="text-sm text-ink-soft">No clauses extracted yet.</p>}
                {clauses.map((c) => (
                  <div key={c.id} onMouseEnter={() => setHighlightText(c.original_text || c.section_label)} onMouseLeave={() => setHighlightText(null)}>
                    {/* USP 3: pass documentId so ClauseCard can fetch negotiation tips */}
                    <ClauseCard clause={c} documentId={id} />
                  </div>
                ))}
              </div>
            )}

            {tab === "Risks" && (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="font-display text-2xl text-ink">Risk scan</h2>
                </div>
                {risks.length === 0 && <p className="text-sm text-ink-soft">No risk findings yet.</p>}
                {risks.map((r) => (
                  <div key={r.id} onMouseEnter={() => setHighlightText(r.clause_snippet || r.section_label)} onMouseLeave={() => setHighlightText(null)}>
                    <RiskCard risk={r} />
                  </div>
                ))}

                <div className="rule pt-6 mt-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-display text-lg text-ink">Action checklist</h3>
                    {checklist.length === 0 && (
                      <button onClick={generateChecklist} className="text-xs font-medium text-accent hover:underline">
                        Generate checklist
                      </button>
                    )}
                  </div>
                  <ul>
                    {checklist.map((item) => (
                      <ChecklistItemRow key={item.id} item={item} onToggle={toggleItem} />
                    ))}
                  </ul>
                </div>

                <div className="rule pt-6 mt-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-display text-lg text-ink">Prepare for legal consultation</h3>
                    {!lawyerPrep && (
                      <button onClick={generateLawyerPrepNow} className="text-xs font-medium text-accent hover:underline">
                        Generate
                      </button>
                    )}
                  </div>
                  {lawyerPrep && (
                    <div className="space-y-4">
                      <div>
                        <p className="text-xs font-medium text-accent mb-1">Summary for your lawyer</p>
                        <p className="text-sm text-ink leading-relaxed">{lawyerPrep.summary_for_lawyer}</p>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-accent mb-1">Questions to ask</p>
                        <ol className="text-sm text-ink space-y-1.5 list-decimal list-inside">
                          {lawyerPrep.questions?.map((q, i) => <li key={i}>{q}</li>)}
                        </ol>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-accent mb-1">Documents to bring</p>
                        <ul className="text-sm text-ink-soft space-y-1 list-disc list-inside">
                          {lawyerPrep.documents_to_bring?.map((d, i) => <li key={i}>{d}</li>)}
                        </ul>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {tab === "Obligations" && analysis && (
              <div className="grid sm:grid-cols-2 gap-8">
                <div>
                  <h3 className="font-display text-lg text-ink mb-3">Your responsibilities</h3>
                  <ul className="text-sm text-ink space-y-2">
                    {analysis.your_obligations?.map((o, i) => (
                      <li key={i} className="border-b border-line pb-2">{o}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="font-display text-lg text-ink mb-3">Other party&rsquo;s responsibilities</h3>
                  <ul className="text-sm text-ink space-y-2">
                    {analysis.other_party_obligations?.map((o, i) => (
                      <li key={i} className="border-b border-line pb-2">{o}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}

            {tab === "Timeline" && analysis && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="font-display text-2xl text-ink">Timeline</h2>
                  {/* USP 5: Calendar export button */}
                  {analysis.important_dates?.length > 0 && (
                    <button
                      onClick={downloadCalendar}
                      className="text-xs font-medium text-ink-soft border border-line rounded-md px-3 py-1.5 hover:border-accent hover:text-accent transition-colors"
                    >
                      📅 Export to Calendar
                    </button>
                  )}
                </div>
                <Timeline dates={analysis.important_dates} />
              </div>
            )}

            {tab === "Ask AI" && (
              <div className="h-[65vh]">
                <h2 className="font-display text-2xl text-ink mb-4">Ask my document</h2>
                <ChatPanel documentId={id} />
              </div>
            )}

            <Disclaimer />
          </section>
        </main>
      </div>
    </>
  );
}

function Shell({ children }) {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="max-w-3xl mx-auto px-6 py-16">{children}</main>
    </div>
  );
}
