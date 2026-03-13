"""Deliberation excerpt figure: agent names + truncated review text."""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt

from ..config import DOCS_VALIDATION_OUTPUTS

# Same styling as corpus_figures
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman", "DejaVu Serif", "serif"]
FIGURE_BG = "#FFFFFF"
PALETTE = {"charcoal": "#2D3142", "steel": "#4F5D75"}


def _parse_deliberation_log(log: str) -> list[tuple[str, str]]:
    """Parse '[Agent]: text' blocks; return list of (agent_name, text)."""
    pattern = r"\[([^\]]+)\]:\s*(.*?)(?=\n\n\[|$)"
    matches = re.findall(pattern, log, re.DOTALL)
    return [(name.strip(), text.strip()) for name, text in matches if name.strip()]


def _wrap_text(text: str, width: int = 70) -> str:
    """Wrap text to approximate character width."""
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


def plot_deliberation_excerpt(
    deliberation_log: str,
    out_path: Path | None = None,
    max_chars_per_agent: int = 300,
) -> Path:
    """Plot deliberation excerpt with agent names and truncated reviews.

    Args:
        deliberation_log: String like "[Methodologist]: ...\n\n[Theorist]: ..."
        out_path: Where to save. Default: DOCS_VALIDATION_OUTPUTS/deliberation_excerpt.png
        max_chars_per_agent: Max characters per agent text (default 300).

    Returns:
        Path to saved figure.
    """
    out_path = out_path or DOCS_VALIDATION_OUTPUTS / "deliberation_excerpt.png"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    entries = _parse_deliberation_log(deliberation_log)
    if not entries:
        # Fallback: treat whole log as one block
        entries = [("Committee", deliberation_log[:500])]

    fig, ax = plt.subplots(figsize=(8, 1.5 + 0.5 * len(entries)))
    fig.patch.set_facecolor(FIGURE_BG)
    ax.set_facecolor(FIGURE_BG)
    ax.axis("off")

    y = 1.0
    for name, text in entries:
        truncated = text[:max_chars_per_agent] + ("…" if len(text) > max_chars_per_agent else "")
        wrapped = _wrap_text(truncated, width=70)
        ax.text(0.05, y, f"{name}:", transform=ax.transAxes, fontsize=11, fontweight="bold", color=PALETTE["charcoal"])
        y -= 0.06
        n_lines = wrapped.count("\n") + 1
        ax.text(0.05, y, wrapped, transform=ax.transAxes, fontsize=10, color=PALETTE["steel"], verticalalignment="top")
        y -= 0.06 * n_lines + 0.12

    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
    plt.close()
    return out_path
