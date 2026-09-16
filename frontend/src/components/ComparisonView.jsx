export default function ComparisonView({ comparison }) {
  const { added = [], removed = [], modified = [], plain_summary } = comparison;

  return (
    <div className="space-y-8">
      {plain_summary && (
        <div>
          <p className="text-xs font-medium text-accent mb-1">What changed, in plain language</p>
          <p className="text-sm text-ink leading-relaxed">{plain_summary}</p>
        </div>
      )}

      <div className="grid sm:grid-cols-3 gap-6">
        <div>
          <p className="text-xs uppercase tracking-wide text-positive font-medium mb-3">Added</p>
          {added.length === 0 && <p className="text-sm text-ink-soft">Nothing added.</p>}
          <ul className="space-y-2">
            {added.map((item, i) => (
              <li key={i} className="text-sm text-ink bg-positive-soft rounded-md px-3 py-2">
                + {item}
              </li>
            ))}
          </ul>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-high font-medium mb-3">Removed</p>
          {removed.length === 0 && <p className="text-sm text-ink-soft">Nothing removed.</p>}
          <ul className="space-y-2">
            {removed.map((item, i) => (
              <li key={i} className="text-sm text-ink bg-high-soft rounded-md px-3 py-2">
                − {item}
              </li>
            ))}
          </ul>
        </div>

        <div>
          <p className="text-xs uppercase tracking-wide text-attention font-medium mb-3">Modified</p>
          {modified.length === 0 && <p className="text-sm text-ink-soft">Nothing modified.</p>}
          <ul className="space-y-2">
            {modified.map((item, i) => (
              <li key={i} className="text-sm text-ink bg-attention-soft rounded-md px-3 py-2">
                <span className="font-medium">{item.aspect}: </span>
                {item.before} → {item.after}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
