"""Deliberation metrics: perspective shifts, challenges, reconciliations (societies of thought)."""
import re


def societies_of_thought_metrics(log: str) -> dict[str, int]:
    """Extract simple counts from a deliberation log (stub / regex-based).

    Args:
        log: Concatenated committee reviews or deliberation transcript.

    Returns:
        Dict with perspective_shifts, challenges, reconciliations (counts).
    """
    perspective_shifts = len(re.findall(r"(?:however|but|alternatively|on the other hand|from another angle)", log, re.I))
    challenges = len(re.findall(r"(?:challenge|weakness|concern|question|critique)", log, re.I))
    reconciliations = len(re.findall(r"(?:synthesis|consensus|agree|balance|together)", log, re.I))
    return {
        "perspective_shifts": perspective_shifts,
        "challenges": challenges,
        "reconciliations": reconciliations,
    }
