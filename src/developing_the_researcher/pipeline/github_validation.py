"""GitHub longitudinal validation: fetch memos, embed, compute trajectories, save results."""
import json

import numpy as np

from ..config import GITHUB_ISSUES_PATH, GITHUB_VALIDATION_PATH
from ..data import GitHubIssuesLoader
from ..models import EmbeddingLoader


def build_memo_panel(corpus: list[dict]) -> list[dict]:
    """Build panel: list of {author, week, memo_text, issue_id, created_at, thumbs_up}.
    Filter: keep memos with len(memo_text) >= 100."""
    panel = []
    for c in corpus:
        text = c.get("memo_text", "") or ""
        if len(text) < 100:
            continue
        panel.append({
            "author": c.get("author", "unknown"),
            "week": c.get("week", 0),
            "memo_text": text,
            "issue_id": c.get("issue_id"),
            "created_at": c.get("created_at", ""),
            "thumbs_up": c.get("thumbs_up", 0),
        })
    return panel


def get_authors_with_both_weeks(
    panel: list[dict],
    early_week: int = 1,
    late_week: int = 9,
) -> list[str]:
    """Return authors who have memos in both early_week and late_week.
    If early_week has no data, use earliest available week; if late_week has none, use latest."""
    by_author_week: dict[str, set[int]] = {}
    for p in panel:
        a = p.get("author", "unknown")
        w = p.get("week", 0)
        if a and w:
            by_author_week.setdefault(a, set()).add(w)
    weeks_present = set()
    for s in by_author_week.values():
        weeks_present.update(s)
    if not weeks_present:
        return []
    early = early_week if early_week in weeks_present else min(weeks_present)
    late = late_week if late_week in weeks_present else max(weeks_present)
    result = [
        a for a, weeks in by_author_week.items()
        if early in weeks and late in weeks
    ]
    return result


def validate_panel(panel: list[dict]) -> dict:
    """Validate panel; return {n_authors, n_memos, weeks_present, authors_with_both}."""
    authors = {p.get("author", "unknown") for p in panel if p.get("author")}
    weeks = {p.get("week", 0) for p in panel if p.get("week")}
    authors_with_both = set(get_authors_with_both_weeks(panel))
    return {
        "n_authors": len(authors),
        "n_memos": len(panel),
        "weeks_present": sorted(weeks),
        "authors_with_both": len(authors_with_both),
    }


def run_github_validation(force_refresh: bool = False) -> dict:
    """Load or fetch GitHub memo corpus, embed, compute trajectories, save to data/github_validation.json."""
    gh = GitHubIssuesLoader()
    if not GITHUB_ISSUES_PATH.exists() or force_refresh:
        corpus = gh.load_github_corpus(force_refresh=True)
    else:
        corpus = gh.load_github_corpus(force_refresh=False)
    gh.close()

    if not corpus:
        out = {"corpus_size": 0, "trajectories": [], "message": "No memo comments in corpus."}
        GITHUB_VALIDATION_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
        return out

    embed_loader = EmbeddingLoader()
    texts = [c.get("memo_text", "")[:2000] for c in corpus]
    embeddings = embed_loader.get_embeddings(texts)

    # Attach embeddings and week for trajectory
    for i, c in enumerate(corpus):
        c["embedding"] = embeddings[i].tolist() if hasattr(embeddings[i], "tolist") else list(embeddings[i])
    by_week: dict[int, list] = {}
    for c in corpus:
        w = c.get("week", 0)
        by_week.setdefault(w, []).append(c)

    trajectories = []
    for week in sorted(by_week.keys()):
        items = by_week[week]
        if len(items) < 2:
            trajectories.append({"week": week, "n": len(items), "mean_sim_to_first": 1.0})
            continue
        first_emb = np.array(items[0]["embedding"])
        sims = [
            embed_loader.cosine_sim(first_emb, np.array(it["embedding"])) for it in items[1:]
        ]
        trajectories.append({
            "week": week,
            "n": len(items),
            "mean_sim_to_first": float(sum(sims) / len(sims)) if sims else 1.0,
        })

    out = {
        "corpus_size": len(corpus),
        "trajectories": trajectories,
        "weeks": sorted(by_week.keys()),
    }
    GITHUB_VALIDATION_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out
