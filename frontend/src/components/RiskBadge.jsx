const LEVELS = {
  high: { label: "High attention", text: "text-high", bg: "bg-high-soft", dot: "bg-high" },
  medium: { label: "Review carefully", text: "text-attention", bg: "bg-attention-soft", dot: "bg-attention" },
  low: { label: "Worth checking", text: "text-attention", bg: "bg-attention-soft", dot: "bg-attention" },
  standard: { label: "Standard", text: "text-positive", bg: "bg-positive-soft", dot: "bg-positive" },
};

export default function RiskBadge({ level }) {
  const cfg = LEVELS[level] || LEVELS.standard;
  return (
    <span
      className={`inline-flex items-center gap-1.5 ${cfg.bg} ${cfg.text} text-xs font-medium px-2.5 py-1 rounded-full`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
      {cfg.label}
    </span>
  );
}
