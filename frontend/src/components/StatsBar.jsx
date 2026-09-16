/**
 * USP 4: StatsBar
 * Shows aggregate stats across all analyzed documents.
 * Renders a pure-SVG donut chart for risk breakdown and stat cards.
 */
import { useEffect, useState } from "react";
import { api } from "../services/api";

function DonutChart({ high, medium, low, standard }) {
  const total = high + medium + low + standard || 1;
  const r = 28;
  const cx = 36;
  const cy = 36;
  const circumference = 2 * Math.PI * r;

  // segments: [value, color]
  const segments = [
    [high, "#ef4444"],
    [medium, "#f59e0b"],
    [low, "#84cc16"],
    [standard, "#94a3b8"],
  ];

  let offset = 0;
  const arcs = segments.map(([val, color]) => {
    const dashLen = (val / total) * circumference;
    const dashGap = circumference - dashLen;
    const arc = (
      <circle
        key={color}
        cx={cx}
        cy={cy}
        r={r}
        fill="none"
        stroke={color}
        strokeWidth="10"
        strokeDasharray={`${dashLen} ${dashGap}`}
        strokeDashoffset={-offset}
        style={{ transform: "rotate(-90deg)", transformOrigin: `${cx}px ${cy}px` }}
      />
    );
    offset += dashLen;
    return arc;
  });

  return (
    <svg width="72" height="72" viewBox="0 0 72 72">
      {/* background track */}
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#e2e8f0" strokeWidth="10" />
      {arcs}
      <text x={cx} y={cy + 1} textAnchor="middle" dominantBaseline="middle" fontSize="11" fontWeight="600" fill="#1e293b">
        {high + medium + low + standard}
      </text>
    </svg>
  );
}

export default function StatsBar() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.getStats().then(setStats).catch(() => {});
  }, []);

  if (!stats || stats.total_documents === 0) return null;

  const { total_documents, analyzed_documents, total_risk_findings, risk_breakdown, avg_attention_score, total_clauses } = stats;
  const { high, medium, low, standard } = risk_breakdown || {};

  return (
    <div className="border border-line rounded-lg p-5 mb-10">
      <p className="text-xs uppercase tracking-wide text-ink-soft mb-4">Your document portfolio</p>
      <div className="flex flex-wrap items-center gap-6">
        {/* Donut chart */}
        <div className="flex items-center gap-3">
          <DonutChart high={high} medium={medium} low={low} standard={standard} />
          <div className="space-y-1 text-xs">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#ef4444]" />
              <span className="text-ink-soft">High: <strong className="text-ink">{high}</strong></span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#f59e0b]" />
              <span className="text-ink-soft">Medium: <strong className="text-ink">{medium}</strong></span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#84cc16]" />
              <span className="text-ink-soft">Low: <strong className="text-ink">{low}</strong></span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-[#94a3b8]" />
              <span className="text-ink-soft">Standard: <strong className="text-ink">{standard}</strong></span>
            </div>
          </div>
        </div>

        {/* Stat cards */}
        <div className="flex flex-wrap gap-4 text-center flex-1">
          {[
            { label: "Documents", value: total_documents },
            { label: "Analyzed", value: analyzed_documents },
            { label: "Risk findings", value: total_risk_findings },
            { label: "Clauses extracted", value: total_clauses },
            { label: "Avg attention score", value: `${avg_attention_score}` },
          ].map(({ label, value }) => (
            <div key={label} className="border border-line rounded-lg px-4 py-3 min-w-[80px]">
              <p className="text-lg font-bold text-ink">{value}</p>
              <p className="text-[10px] text-ink-soft">{label}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
