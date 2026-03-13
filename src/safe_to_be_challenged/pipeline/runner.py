"""Orchestrates: load data -> run experiment -> save results."""
import json

from ..config import CONDITIONS, FIGURES_DIR, PILOT_RESULTS_PATH, QUALITATIVE_SAMPLES_PATH
from ..data import CorpusLoader, DoublesLoader
from ..metrics import mechanical_reliance, quality_rating, trust_rating
from ..models import CommitteeLoader, EmbeddingLoader, SafetyLoader


def run_pilot(
    n_per_condition: int = 2,
    use_github: bool = False,
    save_figures: bool = True,
) -> list[dict]:
    """Run the Memo W9 pilot: three conditions, digital doubles, harmlessness monitor."""
    # Load data
    corpus = CorpusLoader()
    doubles_loader = DoublesLoader(corpus)
    doubles = doubles_loader.load_doubles_from_corpus(n_per_condition=n_per_condition)

    # Load models (lazy)
    embed_loader = EmbeddingLoader()
    committee = CommitteeLoader()
    safety = SafetyLoader(committee)

    def get_feedback(d):
        q = committee.skill_diagnostician(d["thesis"])
        critique = committee.adversarial_critic(d["thesis"], q)
        if d["condition"] == "committee_only":
            return critique
        return safety.harmlessness_monitor(critique, d["condition"], generate_fn=committee.generate)

    def pure_llm_baseline(thesis):
        return committee.generate(f"Revise this thesis abstract to improve it. {thesis[:400]}", max_new_tokens=200)

    def student_revision(thesis, feedback, d):
        if d["trust_sensitivity"] == "low" and d["condition"] != "visible_label":
            return pure_llm_baseline(thesis)
        prompt = f"Revise this thesis incorporating the feedback. Thesis: {thesis[:350]}\nFeedback: {feedback[:400]}"
        return committee.generate(prompt, max_new_tokens=200)

    # Run
    results = []
    for d in doubles:
        feedback = get_feedback(d)
        rev = student_revision(d["thesis"], feedback, d)
        base = pure_llm_baseline(d["thesis"])

        emb_rev = embed_loader.get_embeddings([rev])[0]
        emb_base = embed_loader.get_embeddings([base])[0]
        mr = mechanical_reliance(emb_rev, emb_base, embed_loader.cosine_sim)
        trust = trust_rating(rev, committee.generate)
        quality = quality_rating(rev, committee.generate)

        results.append({
            "condition": d["condition"],
            "mechanical_reliance": float(mr),
            "trust": trust,
            "quality": quality,
            "thesis": d["thesis"][:500],
            "feedback": feedback[:800],
            "revision": rev[:800],
        })

    # Save
    PILOT_RESULTS_PATH.write_text(json.dumps({"results": results}, indent=2), encoding="utf-8")

    # Qualitative samples: 5–10 feedback–revision pairs for interpretation
    sample_size = min(10, len(results))
    qualitative = [{"condition": r["condition"], "thesis": r["thesis"], "feedback": r["feedback"], "revision": r["revision"]} for r in results[:sample_size]]
    QUALITATIVE_SAMPLES_PATH.write_text(json.dumps({"samples": qualitative}, indent=2), encoding="utf-8")

    # Plots
    if save_figures:
        import numpy as np
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        for i, cond in enumerate(CONDITIONS):
            sub = [r for r in results if r["condition"] == cond]
            if sub:
                axes[0].bar(i, np.mean([r["mechanical_reliance"] for r in sub]), label=cond, alpha=0.8)
                axes[1].bar(i, np.mean([r["trust"] for r in sub]), label=cond, alpha=0.8)
        axes[0].set_xticks(range(len(CONDITIONS)))
        axes[0].set_xticklabels([c.replace("_", "\n") for c in CONDITIONS])
        axes[0].set_ylabel("Mean mechanical reliance")
        axes[0].set_title("Mechanical reliance (lower = less copy-paste)")
        axes[1].set_xticks(range(len(CONDITIONS)))
        axes[1].set_xticklabels([c.replace("_", "\n") for c in CONDITIONS])
        axes[1].set_ylabel("Mean trust (engagement)")
        axes[1].set_title("Trust by condition")
        plt.tight_layout()
        fig.savefig(FIGURES_DIR / "pilot_results.png", dpi=150)
        plt.close()

    return results
