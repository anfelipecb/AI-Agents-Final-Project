"""GitHub memo retrospective validation: Week 1 plan vs Week 9 improvement (GPT-4-mini)."""
from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from ..config import (
    COMPETENCY_DIMENSIONS,
    DOCS_VALIDATION_OUTPUTS,
    GITHUB_MEMO_VALIDATION_PATH,
)
from ..data import GitHubIssuesLoader
from ..models import EmbeddingLoader, OpenAIGenerate
from ..models.committee import assemble_committee, run_committee_deliberation
from ..models.development_plan import development_plan
from ..models.diagnostician import diagnose_competencies

from ..analysis.diagnostician_validation import RADAR_DIM_LABELS
from .github_validation import (
    build_memo_panel,
    get_authors_with_both_weeks,
    validate_panel,
)

# Styling
plt.rcParams["font.family"] = "serif"
FIGURE_BG = "#FFFFFF"
PALETTE = {"charcoal": "#2D3142", "steel": "#4F5D75", "warm_orange": "#EF8354"}

def _load_env() -> None:
    """Load .env from project root."""
    from dotenv import load_dotenv
    root = Path(__file__).resolve().parent.parent.parent
    env_path = root / ".env"
    if env_path.exists():
        load_dotenv(env_path)


def verify_openai() -> bool:
    """Verify OpenAI API works. Returns True if OK."""
    _load_env()
    try:
        gen = OpenAIGenerate()
        out = gen.generate("Say 'OK' if you can read this.", max_new_tokens=10)
        return "ok" in out.lower()
    except Exception as e:
        print(f"OpenAI verification failed: {e}")
        return False


def _get_memo_for_author_week(panel: list[dict], author: str, week: int) -> str | None:
    """Return first memo text for author in week, or None."""
    for p in panel:
        if p.get("author") == author and p.get("week") == week:
            return p.get("memo_text", "")
    return None


def _extract_gap_dimensions(plan: dict) -> list[str]:
    """Extract dimension names from gap_map for judge prompt."""
    gap_map = plan.get("gap_map", [])
    dims = []
    for g in gap_map:
        if isinstance(g, dict) and g.get("dimension"):
            dims.append(g["dimension"])
    return dims or list(COMPETENCY_DIMENSIONS.keys())


def _parse_judge_output(raw: str) -> dict[str, float]:
    """Parse judge JSON output; return {dimension: score}."""
    text = raw.strip()
    for pattern in (r"```(?:json)?\s*([\s\S]*?)```", r"(\{[\s\S]*\})"):
        m = re.search(pattern, text)
        if m:
            text = m.group(1).strip()
            break
    try:
        data = json.loads(text)
        return {k: float(v) for k, v in data.items() if isinstance(v, (int, float))}
    except json.JSONDecodeError:
        return {}


def run_retrospective_validation(force_refresh: bool = False) -> dict:
    """Run retrospective validation: Week 1 plan -> GPT-4-mini judge Week 9 improvement."""
    _load_env()
    gh = GitHubIssuesLoader()
    corpus = gh.load_github_corpus(force_refresh=force_refresh)
    gh.close()

    panel = build_memo_panel(corpus)
    validation = validate_panel(panel)
    authors = get_authors_with_both_weeks(panel)

    if not authors:
        out = {
            "corpus_size": len(corpus),
            "panel_validation": validation,
            "authors_with_both": 0,
            "results": [],
            "message": "No authors with memos in both early and late weeks.",
        }
        from ..config import DATA_DIR
    DATA_DIR.mkdir(parents=True, exist_ok=True)
        GITHUB_MEMO_VALIDATION_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
        return out

    gen = OpenAIGenerate()
    # Wrapper for diagnose/development_plan: (prompt, system_prompt, max_new_tokens) -> str
    def _gen(p: str, s: str | None, m: int) -> str:
        return gen.generate(p, system_prompt=s, max_new_tokens=m)

    results = []
    early_week = validation["weeks_present"][0] if validation["weeks_present"] else 1
    late_week = validation["weeks_present"][-1] if validation["weeks_present"] else 9

    for author in authors:
        memo_early = _get_memo_for_author_week(panel, author, early_week)
        memo_late = _get_memo_for_author_week(panel, author, late_week)
        if not memo_early or not memo_late:
            continue

        # Week 1 pipeline
        profile = diagnose_competencies(memo_early[:800], _gen)
        agents = assemble_committee(profile)
        feedback = run_committee_deliberation(memo_early, agents, gen.generate)
        plan = development_plan(profile, feedback, _gen)
        gap_dims = _extract_gap_dimensions(plan)

        # Judge: Week 9 improvement
        gap_summary = json.dumps([g for g in plan.get("gap_map", []) if isinstance(g, dict)][:5])
        judge_prompt = f"""Given this Week {early_week} development plan gap_map and targets, and this Week {late_week} memo text from the same student, rate 1-5 how much the student improved in each targeted dimension (1=no improvement, 5=clear improvement).

Gap map (dimensions and targets):
{gap_summary}

Week {late_week} memo:
{memo_late[:1500]}

Respond with a JSON object: {{"dimension_name": score, ...}} for each dimension in the gap_map. Use only these dimension keys: {gap_dims if gap_dims else list(COMPETENCY_DIMENSIONS.keys())}."""
        judge_raw = gen.generate(judge_prompt, system_prompt="Output only valid JSON.", max_new_tokens=300)
        improvement_scores = _parse_judge_output(judge_raw)

        results.append({
            "author": author,
            "early_week": early_week,
            "late_week": late_week,
            "profile": profile,
            "plan": plan,
            "improvement_scores": improvement_scores,
        })

    # Aggregate
    all_dims = set()
    for r in results:
        all_dims.update(r.get("improvement_scores", {}).keys())
    mean_by_dim = {}
    for d in all_dims:
        vals = [r["improvement_scores"].get(d) for r in results if r["improvement_scores"].get(d) is not None]
        mean_by_dim[d] = float(np.mean(vals)) if vals else 0.0

    out = {
        "corpus_size": len(corpus),
        "panel_validation": validation,
        "authors_with_both": len(authors),
        "early_week": early_week,
        "late_week": late_week,
        "results": results,
        "mean_improvement_by_dimension": mean_by_dim,
    }
    from ..config import DATA_DIR
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    GITHUB_MEMO_VALIDATION_PATH.write_text(json.dumps(out, indent=2, default=str), encoding="utf-8")
    return out


def plot_memo_validation_results(results: dict, out_path: Path | None = None) -> Path:
    """Bar chart: mean improvement score by dimension."""
    out_path = out_path or DOCS_VALIDATION_OUTPUTS / "github_memo_validation.png"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    mean_by_dim = results.get("mean_improvement_by_dimension", {})
    if not mean_by_dim:
        return out_path

    dims = list(mean_by_dim.keys())
    vals = [mean_by_dim[d] for d in dims]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(range(len(dims)), vals, color=PALETTE["steel"], edgecolor=PALETTE["charcoal"])
    ax.set_xticks(range(len(dims)))
    ax.set_xticklabels([d.replace("_", "\n")[:14] for d in dims], fontsize=9)
    ax.set_ylabel("Mean improvement (1-5)")
    ax.set_title("Retrospective validation: Week 1 plan targets vs Week 9 memo improvement")
    ax.set_facecolor(FIGURE_BG)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
    plt.close()
    return out_path


def plot_memo_embedding_trajectories(
    panel: list[dict],
    embed_loader: EmbeddingLoader,
    out_path: Path | None = None,
) -> Path:
    """t-SNE of memo embeddings, colored by week."""
    out_path = out_path or DOCS_VALIDATION_OUTPUTS / "github_memo_trajectories.png"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    texts = [p.get("memo_text", "")[:2000] for p in panel]
    if len(texts) < 2:
        return out_path

    X = embed_loader.get_embeddings(texts)
    from sklearn.manifold import TSNE
    perplexity = min(30, len(X) - 1)
    xy = TSNE(n_components=2, random_state=42, perplexity=perplexity).fit_transform(X)
    weeks = [p.get("week", 0) for p in panel]
    week_arr = np.array(weeks)

    fig, ax = plt.subplots(figsize=(8, 6))
    sc = ax.scatter(xy[:, 0], xy[:, 1], c=week_arr, cmap="viridis", s=40, alpha=0.7)
    plt.colorbar(sc, ax=ax, label="Week")
    ax.set_xlabel("t-SNE 1")
    ax.set_ylabel("t-SNE 2")
    ax.set_title("Memo embedding trajectories over the quarter")
    ax.set_facecolor(FIGURE_BG)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
    plt.close()
    return out_path


def plot_competency_evolution_by_week(
    panel: list[dict],
    generate_fn,
    out_path: Path | None = None,
    max_per_week: int = 5,
) -> Path:
    """Line chart: mean competency score per dimension per week."""
    out_path = out_path or DOCS_VALIDATION_OUTPUTS / "github_competency_evolution.png"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    def _gen(p: str, s: str | None, m: int) -> str:
        return generate_fn(p, system_prompt=s, max_new_tokens=m)

    by_week: dict[int, list[dict]] = {}
    for p in panel:
        w = p.get("week", 0)
        by_week.setdefault(w, []).append(p)

    dims = list(COMPETENCY_DIMENSIONS.keys())
    week_scores: dict[int, dict[str, list[float]]] = {}
    for week in sorted(by_week.keys()):
        items = by_week[week][:max_per_week]
        scores_by_dim: dict[str, list[float]] = {d: [] for d in dims}
        for item in items:
            text = item.get("memo_text", "")[:800]
            profile = diagnose_competencies(text, _gen)
            for d in dims:
                s = profile.get(d, {}).get("score", 3)
                scores_by_dim[d].append(float(s))
        week_scores[week] = {d: np.mean(v) if v else 0 for d, v in scores_by_dim.items()}

    if not week_scores:
        return out_path

    weeks = sorted(week_scores.keys())
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = plt.cm.tab10(np.linspace(0, 1, len(dims)))
    for i, d in enumerate(dims):
        vals = [week_scores[w].get(d, 0) for w in weeks]
        ax.plot(weeks, vals, "o-", label=d.replace("_", " ")[:20], color=colors[i])
    ax.set_xlabel("Week")
    ax.set_ylabel("Mean score (1-5)")
    ax.set_title("Competency profile evolution by week")
    ax.legend(fontsize=8)
    ax.set_ylim(0, 5.5)
    ax.set_facecolor(FIGURE_BG)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
    plt.close()
    return out_path


def plot_memo_activity_by_week(panel: list[dict], out_path: Path | None = None) -> Path:
    """Bar chart: memos per week."""
    out_path = out_path or DOCS_VALIDATION_OUTPUTS / "github_memo_activity.png"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    by_week: dict[int, int] = {}
    for p in panel:
        w = p.get("week", 0)
        by_week[w] = by_week.get(w, 0) + 1

    if not by_week:
        return out_path

    weeks = sorted(by_week.keys())
    counts = [by_week[w] for w in weeks]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(weeks, counts, color=PALETTE["steel"])
    ax.set_xlabel("Week")
    ax.set_ylabel("Number of memos")
    ax.set_title("Memo activity by week")
    ax.set_facecolor(FIGURE_BG)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
    plt.close()
    return out_path


def run_github_memo_validation_full(force_refresh: bool = False) -> tuple[dict, list[Path]]:
    """Run retrospective validation and generate all figures. Returns (results, paths)."""
    results = run_retrospective_validation(force_refresh=force_refresh)
    paths = []

    # Improvement bar chart
    if results.get("results"):
        p = plot_memo_validation_results(results)
        paths.append(p)
        p = plot_retrospective_improvement_heatmap(results)
        paths.append(p)

    # Graphic analysis (need panel)
    gh = GitHubIssuesLoader()
    corpus = gh.load_github_corpus(force_refresh=False)
    gh.close()
    panel = build_memo_panel(corpus)
    if panel:
        embed_loader = EmbeddingLoader()
        p = plot_memo_embedding_trajectories(panel, embed_loader)
        paths.append(p)
        p = plot_memo_activity_by_week(panel)
        paths.append(p)
        gen = OpenAIGenerate()
        p = plot_competency_evolution_by_week(panel, gen.generate, max_per_week=3)
        paths.append(p)

    return results, paths


def plot_retrospective_improvement_heatmap(results: dict, out_path: Path | None = None) -> Path:
    """Heatmap: authors x dimensions, cells = improvement score."""
    out_path = out_path or DOCS_VALIDATION_OUTPUTS / "github_improvement_heatmap.png"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    res_list = results.get("results", [])
    if not res_list:
        return out_path

    all_dims = set()
    for r in res_list:
        all_dims.update(r.get("improvement_scores", {}).keys())
    dims = sorted(all_dims) or list(COMPETENCY_DIMENSIONS.keys())
    authors = [r["author"] for r in res_list]
    data = np.zeros((len(authors), len(dims)))
    for i, r in enumerate(res_list):
        for j, d in enumerate(dims):
            data[i, j] = r.get("improvement_scores", {}).get(d, 0)

    fig, ax = plt.subplots(figsize=(max(6, len(dims) * 1.2), max(4, len(authors) * 0.4)))
    im = ax.imshow(data, aspect="auto", cmap="YlOrRd", vmin=0, vmax=5)
    ax.set_xticks(range(len(dims)))
    ax.set_xticklabels([RADAR_DIM_LABELS.get(d, d.replace("_", " ")[:12]) for d in dims], fontsize=8)
    ax.set_yticks(range(len(authors)))
    ax.set_yticklabels(authors, fontsize=9)
    plt.colorbar(im, ax=ax, label="Improvement (1-5)")
    ax.set_title("Retrospective improvement: author x dimension")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=FIGURE_BG)
    plt.close()
    return out_path
