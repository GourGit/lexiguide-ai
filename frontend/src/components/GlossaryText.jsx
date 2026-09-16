import { memo } from "react";

const GLOSSARY = {
  "indemnify": "To compensate someone for harm or loss.",
  "indemnification": "Compensation for harm or loss.",
  "severability": "A provision keeping the rest of a contract valid even if one part is illegal.",
  "jurisdiction": "The official power to make legal decisions and judgments.",
  "arbitration": "Resolving a dispute outside of court by an impartial third party.",
  "proprietary": "Relating to an owner or ownership, often applied to confidential company information.",
  "liability": "Being legally responsible for something.",
  "without cause": "Firing an employee for no specific reason (not for misconduct).",
  "intellectual property": "Creations of the mind, such as inventions, designs, or code.",
  "non-compete": "A clause preventing an employee from working for a competitor.",
  "waives": "Voluntarily gives up a legal right.",
};

export default memo(function GlossaryText({ text }) {
  if (!text) return null;

  // Split text by words but keep punctuation
  const words = text.split(/\b/);

  return (
    <span>
      {words.map((word, index) => {
        const lowerWord = word.toLowerCase();
        // Check if word (or phrase if we extended regex) is in glossary
        if (GLOSSARY[lowerWord]) {
          return (
            <span
              key={index}
              className="border-b border-dashed border-ink-soft cursor-help relative group text-ink font-medium"
              title={GLOSSARY[lowerWord]}
            >
              {word}
              {/* Custom tooltip could go here, but native title attribute works for a11y */}
            </span>
          );
        }
        return word;
      })}
    </span>
  );
});
