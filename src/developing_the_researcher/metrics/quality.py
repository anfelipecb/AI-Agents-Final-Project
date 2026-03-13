"""Plan quality: LLM judge rates development plan on specificity, actionability, developmental framing."""
from typing import Any, Callable

from .core import extract_rating


def development_plan_quality(
    plan: dict[str, Any],
    generate_fn: Callable[..., str],
    max_new_tokens: int = 150,
) -> dict[str, int]:
    """LLM judge rates a development plan on three dimensions (1-5 each).

    Args:
        plan: Dict with gap_map, exercises, trajectory (from development_plan).
        generate_fn: LLM generate function (e.g. committee.generate).
        max_new_tokens: Max tokens for judge response.

    Returns:
        Dict with keys: specificity, actionability, developmental_framing (each 1-5).
    """
    trajectory = plan.get("trajectory", "")
    exercises = plan.get("exercises", [])
    gap_map = plan.get("gap_map", [])
    summary = f"Trajectory: {trajectory[:400]}\nExercises: {exercises}\nGap map: {gap_map}"
    prompt = f"""Rate this development plan (1-5) on three dimensions. Reply with three numbers on one line: specificity actionability developmental_framing.
Plan summary: {summary[:600]}"""
    out = generate_fn(prompt, None, max_new_tokens)
    nums = [int(x) for x in out.replace(",", " ").split() if x.strip().isdigit()][:3]
    while len(nums) < 3:
        nums.append(3)
    return {
        "specificity": max(1, min(5, nums[0])),
        "actionability": max(1, min(5, nums[1])),
        "developmental_framing": max(1, min(5, nums[2])),
    }
