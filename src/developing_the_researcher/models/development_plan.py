"""Development plan generator: gap map, exercises, trajectory from profile + feedback."""
import json
import re
from typing import Any, Callable


def development_plan(
    profile: dict[str, Any],
    feedback: str,
    generate_fn: Callable[[str, str | None, int], str],
    max_new_tokens: int = 600,
) -> dict[str, Any]:
    """Produce a development plan from competency profile and committee feedback.

    Args:
        profile: Competency diagnosis (e.g. from diagnose_competencies): dimension -> {score, justification}.
        feedback: Consolidated committee feedback text.
        generate_fn: Function (prompt, system_prompt, max_new_tokens) -> str.
        max_new_tokens: Max tokens for LLM response.

    Returns:
        Dict with: gap_map (list or dict of gaps), exercises (list of concrete exercises),
        trajectory (short narrative or steps for development).
    """
    profile_summary = _summarize_profile(profile)
    prompt = f"""Given this competency profile and committee feedback, produce a development plan.

Competency profile (scores 1-5 and brief justifications):
{profile_summary}

Committee feedback:
{feedback[:1500]}

Respond with a single JSON object with exactly these keys:
- "gap_map": list of {{"dimension": str, "current": str, "target": str, "priority": str}} for main gaps
- "exercises": list of {{"title": str, "description": str, "dimension": str}} (2-4 concrete exercises)
- "trajectory": string describing recommended development trajectory (2-4 sentences)

Output only valid JSON, no markdown."""
    system = "You are a thesis advisor creating a developmental plan. Output only valid JSON."
    raw = generate_fn(prompt, system, max_new_tokens)
    text = raw.strip()
    for pattern in (r"```(?:json)?\s*([\s\S]*?)```", r"(\{[\s\S]*\})"):
        m = re.search(pattern, text)
        if m:
            text = m.group(1).strip()
            break
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {"gap_map": [], "exercises": [], "trajectory": "Development plan could not be generated."}
    return {
        "gap_map": data.get("gap_map", []) if isinstance(data.get("gap_map"), list) else [],
        "exercises": data.get("exercises", []) if isinstance(data.get("exercises"), list) else [],
        "trajectory": str(data.get("trajectory", "")),
    }


def _summarize_profile(profile: dict[str, Any]) -> str:
    lines = []
    for dim, val in profile.items():
        if isinstance(val, dict):
            s, j = val.get("score", "?"), val.get("justification", "")
            lines.append(f"- {dim}: score={s}; {j}")
        else:
            lines.append(f"- {dim}: {val}")
    return "\n".join(lines) if lines else str(profile)
