"""Committee assembly visualization: thesis → profile → committee for 2–3 theses."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ..config import COMPETENCY_DIMENSIONS, DOCS_VALIDATION_OUTPUTS
from ..models.diagnostician import diagnose_competencies

# Same styling as corpus_figures
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman", "DejaVu Serif", "serif"]
FIGURE_BG = "#FFFFFF"
PALETTE = {"charcoal": "#2D3142", "warm_orange": "#EF8354", "steel": "#4F5D75"}


def _text_for_thesis(thesis: dict) -> str:
    """Extract thesis text for diagnosis (title + abstract)."""
    title = thesis.get("title") or ""
    abstract = thesis.get("abstract") or ""
    return f"{title}. {abstract}"[:800].strip() or "empty"


def _scores_from_profile(profile: dict) -> list[float]:
    """Extract score list in COMPETENCY_DIMENSIONS order."""
    dims = list(COMPETENCY_DIMENSIONS.keys())
    return [float(profile.get(d, {}).get("score", 3)) for d in dims]


def plot_committee_assembly_demo(
    theses_or_profiles: list[dict],
    committee,
    out_path: Path | None = None,
) -> Path:
    """Plot thesis → profile → committee for 2–3 theses.

    Args:
        theses_or_profiles: List of thesis dicts (with title, abstract) or pre-computed
            profiles (with keys from COMPETENCY_DIMENSIONS). If thesis dicts, run
            diagnose_competencies for each.
        committee: CommitteeLoader instance with assemble_committee and generate.
        out_path: Where to save the figure. Default: DOCS_VALIDATION_OUTPUTS/committee_assembly_demo.png

    Returns:
        Path to saved figure.
    """
    out_path = out_path or DOCS_VALIDATION_OUTPUTS / "committee_assembly_demo.png"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    def generate_fn(prompt: str, system_prompt: str | None, max_new_tokens: int) -> str:
        return committee.generate(prompt, system_prompt=system_prompt, max_new_tokens=max_new_tokens)

    rows: list[dict] = []
    for item in theses_or_profiles:
        if "argument_construction" in item or "methodological_reasoning" in item:
            profile = item
            title = item.get("title", "Pre-computed profile") or "Pre-computed profile"
        else:
            text = _text_for_thesis(item)
            if not text or text == "empty":
                continue
            profile = diagnose_competencies(text, generate_fn)
            title = (item.get("title") or "Untitled")[:60]

        agents = committee.assemble_committee(profile)
        agent_names = [a["name"] for a in agents]
        scores = _scores_from_profile(profile)
        rows.append({"title": title, "profile": profile, "scores": scores, "agents": agent_names})

    n = len(rows)
    if n == 0:
        raise ValueError("No valid theses or profiles to plot")

    dims = list(COMPETENCY_DIMENSIONS.keys())
    dim_labels = [d.replace("_", "\n")[:14] for d in dims]

    fig, axes = plt.subplots(n, 2, figsize=(10, 3.5 * n), squeeze=False)
    fig.patch.set_facecolor(FIGURE_BG)

    for i, row in enumerate(rows):
        ax_bar, ax_comm = axes[i, 0], axes[i, 1]

        # Left: bar chart of 6 scores
        ax_bar.bar(range(len(dims)), row["scores"], color=PALETTE["steel"], edgecolor=PALETTE["charcoal"], linewidth=0.5)
        ax_bar.set_xticks(range(len(dims)))
        ax_bar.set_xticklabels(dim_labels, fontsize=8, rotation=15, ha="right")
        ax_bar.set_ylim(0, 5.5)
        ax_bar.set_ylabel("Score")
        ax_bar.set_title(f"Thesis: {row['title'][:50]}{'…' if len(row['title']) > 50 else ''}", fontsize=10)
        ax_bar.set_facecolor(FIGURE_BG)
        ax_bar.spines["top"].set_visible(False)
        ax_bar.spines["right"].set_visible(False)

        # Right: committee composition
        ax_comm.axis("off")
        ax_comm.set_title("Committee", fontsize=10)
        agent_text = "\n".join(f"• {name}" for name in row["agents"])
        ax_comm.text(0.1, 0.5, agent_text, transform=ax_comm.transAxes, fontsize=11, verticalalignment="center")

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
    plt.close()
    return out_path
