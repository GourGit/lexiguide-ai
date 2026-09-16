import { useState, memo } from "react";
import { api } from "../services/api";
import GlossaryText from "./GlossaryText";

const ClauseCard = memo(function ClauseCard({ clause, documentId }) {
  const [open, setOpen] = useState(false);
  const [tips, setTips] = useState(clause.negotiation_tips || null);
  const [tipsLoading, setTipsLoading] = useState(false);
  const [tipsError, setTipsError] = useState(null);

  async function fetchTips() {
    if (tips || tipsLoading || !documentId) return;
    setTipsLoading(true);
    setTipsError(null);
    try {
      const result = await api.getNegotiationTips(documentId, clause.id);
      setTips(result.tips || []);
    } catch (err) {
      setTipsError(err.message || "Could not load negotiation tips.");
    } finally {
      setTipsLoading(false);
    }
  }

  return (
    <div className="rule py-5">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between text-left group"
      >
        <div>
          <span className="text-xs uppercase tracking-wide text-ink-soft">
            {clause.section_label}
          </span>
          <h4 className="font-display text-lg text-ink mt-0.5">{clause.clause_type}</h4>
        </div>
        <span className="text-ink-soft text-xl leading-none group-hover:text-ink transition-colors">
          {open ? "−" : "+"}
        </span>
      </button>

      {open && (
        <div className="mt-4 space-y-4">
          <blockquote className="text-sm text-ink-soft italic border-l-2 border-line pl-4">
            &ldquo;{clause.original_text}&rdquo;
          </blockquote>

          <div>
            <p className="text-sm font-medium text-ink mb-1">In plain English</p>
            <p className="text-sm text-ink-soft leading-relaxed"><GlossaryText text={clause.plain_explanation} /></p>
          </div>

          <div>
            <p className="text-xs font-medium text-accent mb-1">Why it matters</p>
            <p className="text-sm text-ink leading-relaxed">{clause.why_it_matters}</p>
          </div>

          {clause.what_to_check?.length > 0 && (
            <div>
              <p className="text-xs font-medium text-accent mb-1">What to check</p>
              <ul className="text-sm text-ink-soft space-y-1 list-disc list-inside">
                {clause.what_to_check.map((q, i) => (
                  <li key={i}>{q}</li>
                ))}
              </ul>
            </div>
          )}

          {/* USP 3: Negotiation tips section */}
          {documentId && (
            <div className="border border-line rounded-md p-4 bg-paper-dim/40">
              <div className="flex items-center justify-between mb-2">
                <p className="text-xs font-medium text-ink">💡 Negotiation tips</p>
                {!tips && !tipsLoading && (
                  <button
                    onClick={fetchTips}
                    className="text-xs font-medium text-accent hover:underline"
                  >
                    Get tips →
                  </button>
                )}
              </div>

              {tipsLoading && (
                <p className="text-xs text-ink-soft">Generating negotiation tips…</p>
              )}
              {tipsError && (
                <p className="text-xs text-high">{tipsError}</p>
              )}
              {tips && tips.length === 0 && (
                <p className="text-xs text-ink-soft">No specific negotiation tips for this clause.</p>
              )}
              {tips && tips.length > 0 && (
                <div className="space-y-3">
                  {tips.map((tip, i) => (
                    <div key={i} className="space-y-1">
                      <p className="text-xs font-semibold text-ink">{tip.title}</p>
                      <p className="text-xs text-ink-soft leading-relaxed">{tip.suggestion}</p>
                      {tip.example_phrasing && (
                        <blockquote className="text-xs text-accent italic border-l-2 border-accent/30 pl-2 mt-1">
                          &ldquo;{tip.example_phrasing}&rdquo;
                        </blockquote>
                      )}
                    </div>
                  ))}
                </div>
              )}
              {!tips && !tipsLoading && !tipsError && (
                <p className="text-xs text-ink-soft">
                  Get AI-powered negotiation angles for this clause.
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
});

export default ClauseCard;
