"""Side-by-side feedback comparison: C1 (single agent) vs C3 (prescribed committee)."""
from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt

from ..config import DOCS_VALIDATION_OUTPUTS
from ..models.diagnostician import diagnose_competencies

from .deliberation_figure import plot_deliberation_excerpt

# Same styling as corpus_figures
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman", "DejaVu Serif", "serif"]
FIGURE_BG = "#FFFFFF"
PALETTE = {"charcoal": "#2D3142", "steel": "#4F5D75"}


def _text_for_thesis(thesis: dict) -> str:
    title = thesis.get("title") or ""
    abstract = thesis.get("abstract") or ""
    return f"{title}. {abstract}"[:600].strip() or "empty"


def _thesis_id(thesis: dict, index: int) -> str:
    """Stable id for filename."""
    tid = thesis.get("id") or thesis.get("handle") or str(index)
    return re.sub(r"[^\w\-]", "_", str(tid))[:40]


def _wrap_text(text: str, width: int = 55) -> str:
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


def run_side_by_side_comparison(
    theses: list[dict],
    committee,
    embed_loader=None,
    out_dir: Path | None = None,
) -> list[Path]:
    """Run C1 and C3 for 2–3 theses; save side-by-side figure and deliberation excerpt per thesis.

    Args:
        theses: List of thesis dicts (title, abstract).
        committee: CommitteeLoader with generate, assemble_committee, committee_deliberation.
        embed_loader: Unused (kept for API compatibility).
        out_dir: Output directory. Default: DOCS_VALIDATION_OUTPUTS.

    Returns:
        List of paths to saved files.
    """
    out_dir = Path(out_dir or DOCS_VALIDATION_OUTPUTS)
    out_dir.mkdir(parents=True, exist_ok=True)

    def _generate(prompt: str, system_prompt: str | None, max_new_tokens: int) -> str:
        return committee.generate(prompt, system_prompt=system_prompt, max_new_tokens=max_new_tokens)

    saved: list[Path] = []
    for i, thesis_dict in enumerate(theses):
        thesis_text = _text_for_thesis(thesis_dict)
        if not thesis_text or thesis_text == "empty":
            continue
        tid = _thesis_id(thesis_dict, i)

        # C1: single agent
        c1_feedback = committee.generate(
            f"Review this thesis abstract and give constructive feedback in 2-4 sentences. Thesis: {thesis_text[:500]}",
            system_prompt="You are a helpful thesis advisor.",
            max_new_tokens=200,
        )

        # C3: prescribed committee
        profile = diagnose_competencies(thesis_text, _generate)
        agents = committee.assemble_committee(profile)
        deliberation_log_parts = []
        for a in agents:
            rev = committee.generate(
                f"Review this thesis and give brief feedback. Thesis: {thesis_text[:600]}",
                system_prompt=a["system_prompt"],
                max_new_tokens=200,
            )
            deliberation_log_parts.append(f"[{a['name']}]: {rev}")
        deliberation_log = "\n\n".join(deliberation_log_parts)
        c3_feedback = committee.committee_deliberation(thesis_text, agents)

        # Save deliberation text for download (Option A)
        delib_txt_path = out_dir / f"deliberation_thesis_{tid}.txt"
        delib_txt_path.write_text(deliberation_log, encoding="utf-8")
        saved.append(delib_txt_path)

        # Side-by-side figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
        fig.patch.set_facecolor(FIGURE_BG)
        for ax in (ax1, ax2):
            ax.set_facecolor(FIGURE_BG)
            ax.axis("off")

        title_short = (thesis_dict.get("title") or "Untitled")[:50]
        ax1.set_title("C1: Single Agent", fontsize=12)
        ax1.text(0.05, 0.95, _wrap_text(c1_feedback[:500]), transform=ax1.transAxes, fontsize=10, verticalalignment="top")
        ax2.set_title("C3: Prescribed Committee", fontsize=12)
        ax2.text(0.05, 0.95, _wrap_text(c3_feedback[:500]), transform=ax2.transAxes, fontsize=10, verticalalignment="top")

        fig.suptitle(f"Thesis: {title_short}{'…' if len(title_short) >= 50 else ''}", fontsize=11, y=1.02)
        plt.tight_layout()
        comp_path = out_dir / f"feedback_comparison_thesis_{tid}.png"
        plt.savefig(comp_path, dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
        plt.close()
        saved.append(comp_path)

        # Deliberation excerpt
        delib_path = out_dir / f"deliberation_thesis_{tid}.png"
        plot_deliberation_excerpt(deliberation_log, out_path=delib_path, max_chars_per_agent=300)
        saved.append(delib_path)

    return saved
