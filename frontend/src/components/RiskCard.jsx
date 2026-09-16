import { memo } from "react";
import RiskBadge from "./RiskBadge";

const RiskCard = memo(function RiskCard({ risk }) {
  return (
    <div className="rule py-5">
      <div className="flex items-start justify-between gap-4 mb-2">
        <h4 className="font-display text-base text-ink">{risk.category}</h4>
        <RiskBadge level={risk.risk_level} />
      </div>
      <p className="text-sm text-ink-soft italic mb-3">&ldquo;{risk.clause_snippet}&rdquo;</p>
      <p className="text-sm text-ink leading-relaxed mb-2">{risk.explanation}</p>
      <p className="text-sm text-ink-soft leading-relaxed mb-3">{risk.why_it_matters}</p>
      {risk.suggested_question && (
        <div className="flex items-start justify-between gap-4 bg-paper-dim rounded-md px-3 py-2">
          <p className="text-sm text-ink">
            <span className="text-accent font-medium">Ask your lawyer: </span>
            {risk.suggested_question}
          </p>
        </div>
      )}
    </div>
  );
});

export default RiskCard;
