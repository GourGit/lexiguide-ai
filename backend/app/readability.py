"""
Pure-Python readability scoring — no external dependencies.

Implements a Flesch Reading Ease approximation:
    score = 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)

Score interpretation:
    90-100  Very easy   (plain English, anyone can understand)
    70-90   Easy
    50-70   Fairly difficult (standard legalese range)
    30-50   Difficult   (most legal contracts)
    0-30    Very difficult (academic/dense legal text)
"""
import re

_SENTENCE_END = re.compile(r"[.!?]+")
_WORD_RE = re.compile(r"[a-zA-Z]+")
_VOWEL_RE = re.compile(r"[aeiouy]+", re.IGNORECASE)


def _count_syllables(word: str) -> int:
    """Approximate syllable count for a single word."""
    word = word.lower().rstrip("e")  # silent-e rule
    syllables = len(_VOWEL_RE.findall(word))
    return max(syllables, 1)


def compute_readability(text: str) -> dict:
    """
    Returns a dict with:
      - score (float, 0–100, higher = easier to read)
      - label (str, human-readable band)
      - word_count (int)
      - avg_sentence_length (float)
      - avg_syllables_per_word (float)
      - interpretation (str, plain-English explanation)
    """
    # Tokenise
    sentences = [s.strip() for s in _SENTENCE_END.split(text) if s.strip()]
    words = _WORD_RE.findall(text)

    n_sentences = max(len(sentences), 1)
    n_words = max(len(words), 1)
    n_syllables = sum(_count_syllables(w) for w in words)

    avg_sentence_length = n_words / n_sentences
    avg_syllables_per_word = n_syllables / n_words

    score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
    score = max(0.0, min(100.0, round(score, 1)))

    if score >= 90:
        label = "Very Easy"
        interpretation = (
            "This document is written in very plain, everyday language. "
            "Most people can read and understand it without legal training."
        )
    elif score >= 70:
        label = "Easy"
        interpretation = (
            "This document is fairly straightforward. "
            "A careful read should give you a good understanding without a lawyer."
        )
    elif score >= 50:
        label = "Moderate"
        interpretation = (
            "This document uses moderately complex language — typical for standard contracts. "
            "Pay special attention to technical or defined terms."
        )
    elif score >= 30:
        label = "Difficult"
        interpretation = (
            "This document is written in dense, complex language typical of legal contracts. "
            "Consider asking a lawyer to walk you through the key clauses."
        )
    else:
        label = "Very Difficult"
        interpretation = (
            "This document uses highly complex legal language. "
            "It is strongly recommended you consult a qualified legal professional before signing."
        )

    return {
        "score": score,
        "label": label,
        "word_count": n_words,
        "avg_sentence_length": round(avg_sentence_length, 1),
        "avg_syllables_per_word": round(avg_syllables_per_word, 2),
        "interpretation": interpretation,
    }
