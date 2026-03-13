"""Development plan example figure: gap_map, exercises, trajectory."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from ..config import DOCS_VALIDATION_OUTPUTS

# Same styling as corpus_figures
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman", "DejaVu Serif", "serif"]
FIGURE_BG = "#FFFFFF"
PALETTE = {"charcoal": "#2D3142", "steel": "#4F5D75"}


def _wrap_text(text: str, width: int = 70) -> str:
    words = text.split()
    lines, current = [], []
    n = 0
    for w in words:
        if n + len(w) + 1 > width:
            if current:
                lines.append(" ".join(current))
            current, n = [w], len(w)
        else:
            current.append(w)
            n += len(w) + 1
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)


def plot_development_plan_example(
    plan_dict: dict,
    thesis_title: str = "Example Thesis",
    out_path: Path | None = None,
) -> Path:
    """Plot development plan: gap map, exercises, trajectory.

    Args:
        plan_dict: From development_plan(); keys: gap_map, exercises, trajectory.
        thesis_title: Short title for figure header.
        out_path: Where to save. Default: DOCS_VALIDATION_OUTPUTS/development_plan_example.png

    Returns:
        Path to saved figure.
    """
    out_path = out_path or DOCS_VALIDATION_OUTPUTS / "development_plan_example.png"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    gap_map = plan_dict.get("gap_map", [])
    exercises = plan_dict.get("exercises", [])
    trajectory = plan_dict.get("trajectory", "")

    # Build text blocks
    gap_lines = []
    for i, g in enumerate(gap_map[:5], 1):
        if isinstance(g, dict):
            dim = g.get("dimension", "?")
            curr = g.get("current", "")
            tgt = g.get("target", "")
            prio = g.get("priority", "")
            gap_lines.append(f"{i}. {dim}: {curr} → {tgt}" + (f" (priority: {prio})" if prio else ""))
        else:
            gap_lines.append(f"{i}. {g}")
    gap_text = "\n".join(gap_lines) if gap_lines else "No gaps identified."

    ex_lines = []
    for i, e in enumerate(exercises[:5], 1):
        if isinstance(e, dict):
            title = e.get("title", "Exercise")
            desc = e.get("description", "")[:120]
            dim = e.get("dimension", "")
            ex_lines.append(f"{i}. {title}" + (f" ({dim})" if dim else "") + f"\n   {desc}")
        else:
            ex_lines.append(f"{i}. {e}")
    ex_text = "\n".join(ex_lines) if ex_lines else "No exercises specified."

    traj_text = _wrap_text(trajectory[:400], width=70) if trajectory else "No trajectory provided."

    fig, axes = plt.subplots(3, 1, figsize=(8, 8))
    fig.patch.set_facecolor(FIGURE_BG)
    fig.suptitle(f"Development Plan: {thesis_title[:50]}{'…' if len(thesis_title) > 50 else ''}", fontsize=12, y=1.02)

    axes[0].set_title("1. Gap Map", fontsize=11)
    axes[0].axis("off")
    axes[0].text(0.05, 0.95, gap_text, transform=axes[0].transAxes, fontsize=9, verticalalignment="top")

    axes[1].set_title("2. Exercises", fontsize=11)
    axes[1].axis("off")
    axes[1].text(0.05, 0.95, ex_text, transform=axes[1].transAxes, fontsize=9, verticalalignment="top")

    axes[2].set_title("3. Trajectory", fontsize=11)
    axes[2].axis("off")
    axes[2].text(0.05, 0.95, traj_text, transform=axes[2].transAxes, fontsize=9, verticalalignment="top")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
    plt.close()
    return out_path
