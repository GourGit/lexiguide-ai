export default function ChecklistItemRow({ item, onToggle }) {
  return (
    <li className="flex items-start gap-3 py-3 rule">
      <button
        onClick={() => onToggle(item)}
        className={`mt-0.5 w-5 h-5 rounded border flex items-center justify-center text-xs shrink-0 transition-colors ${
          item.is_done ? "bg-positive border-positive text-white" : "border-line text-transparent hover:border-accent"
        }`}
      >
        ✓
      </button>
      <div>
        <p className={`text-sm ${item.is_done ? "text-ink-soft line-through" : "text-ink"}`}>{item.text}</p>
        {item.explanation && <p className="text-xs text-ink-soft mt-0.5">{item.explanation}</p>}
      </div>
    </li>
  );
}
