"""GitHub longitudinal validation: fetch memos, embed, compute trajectories, save results."""
import json

import numpy as np

from ..config import GITHUB_ISSUES_PATH, GITHUB_VALIDATION_PATH
from ..data import GitHubIssuesLoader
from ..models import EmbeddingLoader


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
