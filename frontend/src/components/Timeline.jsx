export default function Timeline({ dates = [] }) {
  if (!dates.length) {
    return <p className="text-sm text-ink-soft">No dates or deadlines were extracted from this document.</p>;
  }
  return (
    <ol className="relative">
      {dates.map((d, i) => (
        <li key={i} className="pl-6 pb-6 last:pb-0 relative">
          <span className="absolute left-0 top-1.5 w-2.5 h-2.5 rounded-full bg-accent" />
          {i < dates.length - 1 && (
            <span className="absolute left-[4.5px] top-4 bottom-0 w-px bg-line" />
          )}
          <p className="text-sm font-medium text-ink">{d.label}</p>
          <p className="text-sm text-ink-soft">{d.detail}</p>
        </li>
      ))}
    </ol>
  );
}
