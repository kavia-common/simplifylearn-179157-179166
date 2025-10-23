from dataclasses import dataclass

from src.db.models import LevelEnum


@dataclass
class SimplifiedTexts:
    """Container for simplified results across levels."""
    eli5: str | None
    eli15: str | None
    expert: str | None


def _normalize_text(text: str) -> str:
    """Trim whitespace and normalize spacing."""
    return " ".join(text.strip().split())


# PUBLIC_INTERFACE
def deterministic_simplify(title: str, content: str, level: LevelEnum) -> str:
    """
    Deterministic, rule-based simplification that is:
    - clear
    - shorter
    - jargon-free where possible
    It does not rely on external services to remain deterministic.

    Rules applied:
    - Keep the main idea in one sentence.
    - Prefer short words and remove filler.
    - Add a brief 'Why it matters' clause depending on level.
    """
    title_n = _normalize_text(title)
    content_n = _normalize_text(content)
    # Extract a main idea: pick the first sentence or the first ~24 words
    parts = content_n.split(".")
    first_sentence = parts[0] if parts and len(parts[0]) > 0 else content_n
    words = first_sentence.split()
    main_idea = " ".join(words[:24])

    if level == LevelEnum.ELI5:
        prefix = "Like you're five: "
        why = " It helps us understand the world."
        tip = " Think of it like a simple picture."
    elif level == LevelEnum.ELI15:
        prefix = "Like you're fifteen: "
        why = " This matters because it affects how things work in practice."
        tip = " A quick way to see it is to compare causes and effects."
    else:
        prefix = "For experts: "
        why = " Relevance: improves decisions and system outcomes."
        tip = " Key trade-offs should be stated clearly."

    # Build a very short, jargon-light explanation
    explanation = f"{prefix}{title_n}. In short: {main_idea}."
    # Keep a brief, level-specific addition
    explanation += why
    if level != LevelEnum.EXPERT:
        explanation += tip

    return explanation
