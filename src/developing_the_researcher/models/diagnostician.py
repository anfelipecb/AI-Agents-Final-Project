"""Six-dimension competency diagnostician for thesis assessment."""
import json
import re
from typing import Any, Callable

from ..config import COMPETENCY_DIMENSIONS


def diagnose_competencies(
    thesis: str,
    generate_fn: Callable[[str, str | None, int], str],
    max_new_tokens: int = 512,
) -> dict[str, Any]:
    """Assess thesis on six competency dimensions; return scores (1-5) and justifications.

    Args:
        thesis: Thesis abstract or excerpt to assess.
        generate_fn: Function (prompt, system_prompt, max_new_tokens) -> str.
        max_new_tokens: Max tokens for LLM response.

    Returns:
        Dict with keys: dimension names from COMPETENCY_DIMENSIONS, each mapping to
        {"score": int 1-5, "justification": str}; plus "overall" if present.
    """
    dims_desc = "\n".join(f"- {k}: {v}" for k, v in COMPETENCY_DIMENSIONS.items())
    prompt = f"""Assess this thesis on each competency dimension below. For each dimension, give a score from 1 (weak) to 5 (strong) and a brief justification.

Dimensions:
{dims_desc}

Thesis (excerpt):
{thesis[:800]}

Respond with a single JSON object. Use exactly these dimension keys: {list(COMPETENCY_DIMENSIONS.keys())}. Each value must be an object with "score" (integer 1-5) and "justification" (string). Example:
{{"argument_construction": {{"score": 3, "justification": "..."}}, ...}}"""
    system = "You are a thesis advisor assessing research competency. Output only valid JSON, no markdown."
    raw = generate_fn(prompt, system, max_new_tokens)
    # Extract JSON from response (handle markdown code blocks)
    text = raw.strip()
    for pattern in (r"```(?:json)?\s*([\s\S]*?)```", r"(\{[\s\S]*\})"):
        m = re.search(pattern, text)
        if m:
            text = m.group(1).strip()
            break
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = _fallback_competency_profile()
    # Normalize to expected keys and shape
    result: dict[str, Any] = {}
    for k in COMPETENCY_DIMENSIONS:
        if k in data and isinstance(data[k], dict):
            score = data[k].get("score", 3)
            just = data[k].get("justification", "")
        else:
            score, just = 3, "Assessment unavailable."
        result[k] = {"score": max(1, min(5, int(score) if isinstance(score, (int, float)) else 3)), "justification": str(just)}
    return result


def _fallback_competency_profile() -> dict:
    """Return a neutral profile when JSON parsing fails."""
    return {k: {"score": 3, "justification": "Could not parse diagnostician output."} for k in COMPETENCY_DIMENSIONS}
