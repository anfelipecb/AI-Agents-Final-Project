"""Diagnostician validation: sample theses by embedding cluster, run 6-dim diagnostician, radar charts."""
from __future__ import annotations

import json
import random
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ..config import (
    COMPETENCY_DIMENSIONS,
    DIAGNOSTICIAN_VALIDATION_PATH,
    DOCS_VALIDATION_OUTPUTS,
)
from ..data import CorpusLoader
from ..models import CommitteeLoader, EmbeddingLoader
from ..models.diagnostician import diagnose_competencies

# Same styling as corpus_figures
plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman", "DejaVu Serif", "serif"]
FIGURE_BG = "#FFFFFF"
PALETTE = {"charcoal": "#2D3142", "white": "#FFFFFF"}

# Short labels for radar axes (avoid truncation like "self reflexi", "evidence eva")
RADAR_DIM_LABELS = {
    "argument_construction": "argument",
    "evidence_evaluation": "evidence",
    "methodological_reasoning": "method",
    "theoretical_integration": "theory",
    "self_reflexivity": "reflexivity",
    "receptivity_to_critique": "receptivity",
}

DIAGNOSTICIAN_MODELS = [
    "Qwen/Qwen2.5-0.5B-Instruct",
    "Qwen/Qwen2.5-1.5B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
]


def _text_for_embedding(thesis: dict, use_keywords: bool = False) -> str:
    """Text to embed: abstract (+ title) or keywords joined. Matches corpus_figures.fig_02."""
    if use_keywords and thesis.get("keywords"):
        return " ".join(thesis["keywords"])
    title = thesis.get("title") or ""
    abstract = thesis.get("abstract") or ""
    return f"{title}. {abstract}"[:512].strip() or "empty"


def get_cluster_assignments(
    theses: list[dict],
    embed_loader: EmbeddingLoader,
    n_clusters: int = 6,
    random_state: int = 42,
) -> list[dict]:
    """Assign each thesis a cluster label using same logic as fig_02 (keyword/abstract embeddings, KMeans).

    Returns list of dicts: { "index": int, "cluster": int } for theses that have valid text.
    """
    from sklearn.cluster import KMeans

    texts = [_text_for_embedding(t, use_keywords=True) for t in theses]
    valid = [(i, t) for i, t in enumerate(theses) if texts[i].strip() and texts[i] != "empty"]
    if not valid:
        return []
    idx_list = [i for i, _ in valid]
    X = embed_loader.get_embeddings([texts[i] for i in idx_list])
    n_clusters = min(n_clusters, len(X) - 1) if len(X) > 1 else 1
    if n_clusters < 2:
        return [{"index": idx_list[0], "cluster": 0}]
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state).fit(X)
    labels = kmeans.labels_
    return [{"index": idx_list[j], "cluster": int(labels[j])} for j in range(len(idx_list))]


def sample_theses_by_cluster(
    theses: list[dict],
    embed_loader: EmbeddingLoader,
    n_total: int = 10,
    n_clusters: int = 6,
    random_state: int = 42,
) -> list[dict]:
    """Sample n_total theses spread across clusters (same as fig_02). Returns thesis dicts with 'cluster' key.

    Strategy: at least 1 per cluster when possible; fill remainder proportionally (e.g. 2 from clusters 0-3, 1 from 4-5).
    """
    assignments = get_cluster_assignments(theses, embed_loader, n_clusters=n_clusters, random_state=random_state)
    if not assignments:
        return []
    # Group thesis indices by cluster
    by_cluster: dict[int, list[int]] = {}
    for a in assignments:
        c = a["cluster"]
        if c not in by_cluster:
            by_cluster[c] = []
        by_cluster[c].append(a["index"])
    rng = random.Random(random_state)
    for c in by_cluster:
        rng.shuffle(by_cluster[c])
    # Target: ~2 from first 4 clusters, ~1 from last 2 (or proportional)
    n_per = max(1, n_total // n_clusters)
    remainder = n_total - n_per * n_clusters
    selected: list[tuple[int, int]] = []  # (index, cluster)
    clusters_sorted = sorted(by_cluster.keys())
    for i, c in enumerate(clusters_sorted):
        take = n_per + (1 if i < remainder else 0)
        for _ in range(min(take, len(by_cluster[c]))):
            if by_cluster[c]:
                selected.append((by_cluster[c].pop(0), c))
    if len(selected) < n_total:
        for c in clusters_sorted:
            while len(selected) < n_total and by_cluster[c]:
                selected.append((by_cluster[c].pop(0), c))
    result = []
    for idx, cluster in selected[:n_total]:
        t = dict(theses[idx])
        t["cluster"] = cluster
        result.append(t)
    return result


def _scores_from_profile(profile: dict) -> list[float]:
    """Extract score list in COMPETENCY_DIMENSIONS order."""
    dims = list(COMPETENCY_DIMENSIONS.keys())
    return [float(profile.get(d, {}).get("score", 3)) for d in dims]


def _plot_radar_axes(ax: plt.Axes, dims: list[str]) -> tuple[list[float], list[float]]:
    """Set up polar axes for radar; return angles (rad) and tick positions."""
    n = len(dims)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]
    ax.set_theta_zero_location("N")
    ax.set_xticks(angles[:-1])
    labels = [RADAR_DIM_LABELS.get(d, d.replace("_", " ")[:12]) for d in dims]
    ax.set_xticklabels(labels, size=9, pad=4)
    ax.set_ylim(0, 5)
    ax.set_facecolor(FIGURE_BG)
    ax.figure.patch.set_facecolor(FIGURE_BG)
    return angles, list(range(1, 6))


def plot_radar_per_thesis(
    results: list[dict],
    out_dir: Path,
) -> list[Path]:
    """One radar per thesis: 3 overlaid series (one per model). Saves to out_dir/radar_thesis_{id}.png."""
    dims = list(COMPETENCY_DIMENSIONS.keys())
    n = len(dims)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]
    angles_arr = np.array(angles)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    by_thesis: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        key = r["thesis_id"] + "_" + str(r.get("cluster", ""))
        by_thesis[key].append(r)
    model_colors = ["#E63946", "#2A9D8F", "#264653"]
    for key, rows in by_thesis.items():
        thesis_id = rows[0]["thesis_id"]
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection="polar"))
        _plot_radar_axes(ax, dims)
        for i, row in enumerate(rows):
            scores = _scores_from_profile(row["profile"])
            scores += scores[:1]
            model_short = row["model"].split("/")[-1].replace("-Instruct", "")
            ax.plot(angles_arr, scores, "o-", linewidth=1.5, label=model_short, color=model_colors[i % 3])
            ax.fill(angles_arr, scores, alpha=0.15, color=model_colors[i % 3])
        ax.legend(loc="upper right", fontsize=8)
        ax.set_title(f"Thesis {thesis_id} (cluster {rows[0].get('cluster', '')})", color=PALETTE["charcoal"], pad=20)
        path = out_dir / f"radar_thesis_{thesis_id}.png"
        fig.tight_layout()
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
        plt.close()
        saved.append(path)
    return saved


def plot_radar_by_model(results: list[dict], out_dir: Path) -> Path:
    """One radar: mean scores per model (3 series)."""
    dims = list(COMPETENCY_DIMENSIONS.keys())
    by_model: dict[str, list[list[float]]] = defaultdict(list)
    for r in results:
        by_model[r["model"]].append(_scores_from_profile(r["profile"]))
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection="polar"))
    angles, _ = _plot_radar_axes(ax, dims)
    angles_arr = np.array(angles)
    model_colors = ["#E63946", "#2A9D8F", "#264653"]
    for i, (model, score_lists) in enumerate(sorted(by_model.items())):
        mean_scores = np.array(score_lists).mean(axis=0).tolist()
        mean_scores += mean_scores[:1]
        model_short = model.split("/")[-1].replace("-Instruct", "")
        ax.plot(angles_arr, mean_scores, "o-", linewidth=2, label=model_short, color=model_colors[i % 3])
        ax.fill(angles_arr, mean_scores, alpha=0.2, color=model_colors[i % 3])
    ax.legend(loc="upper right")
    ax.set_title("Mean competency profile by model", color=PALETTE["charcoal"], pad=20)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "radar_by_model.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
    plt.close()
    return path


def plot_radar_by_cluster(results: list[dict], out_dir: Path) -> Path:
    """One radar per cluster: mean scores per cluster (up to 6 series)."""
    dims = list(COMPETENCY_DIMENSIONS.keys())
    by_cluster: dict[int, list[list[float]]] = defaultdict(list)
    for r in results:
        by_cluster[r["cluster"]].append(_scores_from_profile(r["profile"]))
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection="polar"))
    angles, _ = _plot_radar_axes(ax, dims)
    angles_arr = np.array(angles)
    colors = ["#E63946", "#2A9D8F", "#E9C46A", "#264653", "#F4A261", "#9B5DE5"]
    for i, cluster in enumerate(sorted(by_cluster.keys())):
        score_lists = by_cluster[cluster]
        mean_scores = np.array(score_lists).mean(axis=0).tolist()
        mean_scores += mean_scores[:1]
        ax.plot(angles_arr, mean_scores, "o-", linewidth=1.5, label=f"Cluster {cluster}", color=colors[i % len(colors)])
        ax.fill(angles_arr, mean_scores, alpha=0.15, color=colors[i % len(colors)])
    ax.legend(loc="upper right", fontsize=8)
    ax.set_title("Mean competency profile by cluster", color=PALETTE["charcoal"], pad=20)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "radar_by_cluster.png"
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
    plt.close()
    return path


def _save_checkpoint(
    results: list[dict],
    n_theses: int,
    models: list[str],
    out_json_path: Path,
) -> None:
    """Save partial or full results to JSON. Called after each thesis for crash resilience."""
    payload = {
        "run_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "n_theses": n_theses,
        "models": models,
        "results": results,
    }
    out_json_path.parent.mkdir(parents=True, exist_ok=True)
    out_json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_existing_results(out_json_path: Path) -> tuple[list[dict], set[tuple[str, str]]]:
    """Load existing results if present. Returns (results_list, set of (thesis_id, model) already done)."""
    if not out_json_path.exists():
        return [], set()
    try:
        data = json.loads(out_json_path.read_text(encoding="utf-8"))
        results = data.get("results", [])
        done = {(r["thesis_id"], r["model"]) for r in results}
        return results, done
    except (json.JSONDecodeError, KeyError):
        return [], set()


def run_validation(
    corpus_path: Path | None = None,
    n_theses: int = 10,
    models: list[str] | None = None,
    out_json_path: Path | None = None,
    out_figures_dir: Path | None = None,
    random_state: int = 42,
    resume: bool = True,
) -> list[dict]:
    """Sample theses by cluster, run diagnostician with each model, save JSON and radar charts.

    Saves after each thesis and after each model (figures) for crash resilience. If resume=True
    and out_json_path exists, skips (thesis, model) pairs already completed.
    """
    loader = CorpusLoader(path=corpus_path)
    theses = loader.load()
    if not theses:
        return []
    embed_loader = EmbeddingLoader()
    sample = sample_theses_by_cluster(theses, embed_loader, n_total=n_theses, random_state=random_state)
    if not sample:
        return []
    models = models or DIAGNOSTICIAN_MODELS
    out_json_path = out_json_path or DIAGNOSTICIAN_VALIDATION_PATH
    out_figures_dir = out_figures_dir or DOCS_VALIDATION_OUTPUTS

    results, done = _load_existing_results(out_json_path) if resume else ([], set())

    for model_name in models:
        committee = CommitteeLoader(model_name=model_name)

        def generate_fn(p: str, s: str | None, m: int) -> str:
            return committee.generate(p, system_prompt=s, max_new_tokens=m)

        for t in sample:
            thesis_id = str(t.get("id", ""))
            if (thesis_id, model_name) in done:
                continue
            text = f"{t.get('title', '')}. {t.get('abstract', '')}"[:800]
            profile = diagnose_competencies(text, generate_fn)
            row = {
                "thesis_id": thesis_id,
                "title": (t.get("title") or "")[:80],
                "cluster": t["cluster"],
                "model": model_name,
                "profile": profile,
            }
            results.append(row)
            done.add((thesis_id, model_name))
            _save_checkpoint(results, n_theses, models, out_json_path)

        out_figures_dir.mkdir(parents=True, exist_ok=True)
        plot_radar_per_thesis(results, out_figures_dir)
        plot_radar_by_model(results, out_figures_dir)
        plot_radar_by_cluster(results, out_figures_dir)

    return results
