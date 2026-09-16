const CATEGORY_LEVEL = { high: 3, medium: 2, low: 1, standard: 0 };

function levelFromScore(score) {
  if (score >= 66) return { label: "High", cls: "text-high" };
  if (score >= 33) return { label: "Medium", cls: "text-attention" };
  return { label: "Low", cls: "text-positive" };
}

export default function AttentionScore({ score = 0, risks = [] }) {
  const overall = levelFromScore(score);

  const byCategory = {};
  risks.forEach((r) => {
    const cat = r.category || "Other";
    const lvl = CATEGORY_LEVEL[r.risk_level] ?? 0;
    if (!byCategory[cat] || lvl > byCategory[cat]) byCategory[cat] = lvl;
  });
  const rows = Object.entries(byCategory)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6);
  const levelLabel = (n) => (n === 3 ? "High" : n === 2 ? "Medium" : n === 1 ? "Low" : "Standard");
  const levelCls = (n) => (n === 3 ? "text-high" : n === 2 ? "text-attention" : n === 1 ? "text-attention" : "text-positive");
  const barCls = (n) => (n === 3 ? "bg-high" : n === 2 ? "bg-attention" : n === 1 ? "bg-attention" : "bg-positive");

  return (
    <div>
      <div className="flex items-baseline justify-between mb-2">
        <span className="text-sm text-ink-soft">AI Attention Score</span>
        <span className={`text-sm font-medium ${overall.cls}`}>{overall.label} · {score}%</span>
      </div>
      <div className="h-2 rounded-full bg-paper-dim overflow-hidden mb-2">
        <div
          className={`h-full rounded-full ${overall.cls.replace("text-", "bg-")}`}
          style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
        />
      </div>
      <p className="text-xs text-ink-soft mb-5">
        This score indicates clauses that may deserve closer review. It is not a legal risk
        probability.
      </p>

      {rows.length > 0 && (
        <div className="space-y-2.5">
          {rows.map(([cat, lvl]) => (
            <div key={cat} className="flex items-center gap-3">
              <span className="text-sm text-ink w-40 truncate">{cat}</span>
              <div className="flex-1 h-1.5 rounded-full bg-paper-dim overflow-hidden">
                <div
                  className={`h-full rounded-full ${barCls(lvl)}`}
                  style={{ width: `${(lvl / 3) * 100}%` }}
                />
              </div>
              <span className={`text-xs w-16 text-right ${levelCls(lvl)}`}>{levelLabel(lvl)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
