/**
 * USP 2: ReadabilityMeter
 * Displays a Flesch Reading Ease score as a labeled gauge with a color-coded bar.
 * Score 0 = hardest (deep red), 100 = easiest (green).
 */
export default function ReadabilityMeter({ data }) {
  if (!data) return null;

  const { score, label, word_count, avg_sentence_length, interpretation } = data;

  // Color stops: red (0) → orange (30) → yellow (50) → light-green (70) → green (90+)
  function scoreColor(s) {
    if (s >= 70) return "#22c55e";   // green
    if (s >= 50) return "#84cc16";   // lime
    if (s >= 30) return "#f59e0b";   // amber
    return "#ef4444";                 // red
  }

  const color = scoreColor(score);
  const pct = Math.max(2, Math.min(100, score)); // clamp for display

  return (
    <div className="border border-line rounded-lg p-5">
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="text-xs uppercase tracking-wide text-ink-soft mb-0.5">ReadScore</p>
          <h4 className="font-display text-lg text-ink">{label}</h4>
        </div>
        <span
          className="text-3xl font-bold tabular-nums"
          style={{ color }}
        >
          {score}
        </span>
      </div>

      {/* Progress bar */}
      <div className="w-full h-2 rounded-full bg-paper-dim overflow-hidden mb-3">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${pct}%`, background: color }}
        />
      </div>

      {/* Scale labels */}
      <div className="flex justify-between text-[10px] text-ink-soft mb-4">
        <span>Very difficult</span>
        <span>Moderate</span>
        <span>Very easy</span>
      </div>

      <p className="text-xs text-ink-soft leading-relaxed">{interpretation}</p>

      <div className="flex gap-4 mt-3 pt-3 border-t border-line">
        <div className="text-center">
          <p className="text-sm font-medium text-ink">{word_count?.toLocaleString()}</p>
          <p className="text-[10px] text-ink-soft">Words</p>
        </div>
        <div className="text-center">
          <p className="text-sm font-medium text-ink">{avg_sentence_length}</p>
          <p className="text-[10px] text-ink-soft">Avg words/sentence</p>
        </div>
        <div className="text-center">
          <p className="text-sm font-medium text-ink" style={{ color }}>
            {score}/100
          </p>
          <p className="text-[10px] text-ink-soft">ReadScore</p>
        </div>
      </div>
    </div>
  );
}
