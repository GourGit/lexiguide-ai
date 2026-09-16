export default function Disclaimer({ compact = false }) {
  if (compact) {
    return (
      <p className="text-xs text-ink-soft leading-relaxed">
        LexiGuide AI provides informational assistance, not legal advice. For decisions
        involving your legal rights or obligations, consult a qualified legal professional.
      </p>
    );
  }
  return (
    <div className="rule pt-4 mt-8">
      <p className="text-sm text-ink-soft leading-relaxed max-w-2xl">
        LexiGuide AI provides informational assistance, not legal advice. For decisions
        involving your legal rights or obligations, consult a qualified legal professional.
      </p>
    </div>
  );
}
