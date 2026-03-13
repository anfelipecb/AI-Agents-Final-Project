"""Orchestrates: load data -> run experiment (3 conditions) -> save results."""
import json
import random

from ..config import CONDITIONS, FIGURES_DIR, PILOT_RESULTS_PATH, QUALITATIVE_SAMPLES_PATH, STUDENT_PROFILES
from ..data import CorpusLoader, DoublesLoader
from ..metrics import (
    development_plan_quality,
    feedback_specificity,
    mechanical_reliance,
    quality_rating,
    societies_of_thought_metrics,
    trust_rating,
)
from ..models import CommitteeLoader, EmbeddingLoader, SafetyLoader
from ..models.committee import AGENT_PERSONAS
from ..models.development_plan import development_plan
from ..models.diagnostician import diagnose_competencies


def run_pilot(
    n_per_condition: int = 2,
    use_github: bool = False,
    save_figures: bool = True,
    full_experiment: bool = False,
) -> list[dict]:
    """Run pilot: C1 single agent, C2 random committee, C3 prescribed committee."""
    corpus = CorpusLoader()
    doubles_loader = DoublesLoader(corpus)
    n = 5 if full_experiment else n_per_condition
    doubles = doubles_loader.load_doubles_from_corpus(n_per_condition=n, override_fast_mode=full_experiment)

    embed_loader = EmbeddingLoader()
    committee = CommitteeLoader()
    safety = SafetyLoader(committee)

    def _generate(prompt: str, system_prompt: str | None, max_new_tokens: int) -> str:
        return committee.generate(prompt, system_prompt=system_prompt, max_new_tokens=max_new_tokens)

    def get_feedback_and_extras(d: dict) -> tuple[str, dict]:
        """Return (feedback_text, extras dict with profile, committee, deliberation_log, plan)."""
        thesis = d["thesis"]
        condition = d["condition"]
        extras = {}

        if condition == "single_agent":
            feedback = committee.generate(
                f"Review this thesis abstract and give constructive feedback in 2-4 sentences. Thesis: {thesis[:500]}",
                system_prompt="You are a helpful thesis advisor.",
                max_new_tokens=200,
            )
            return feedback, extras

        if condition == "random_committee":
            agents = random.sample(AGENT_PERSONAS, min(3, len(AGENT_PERSONAS)))
            deliberation_log = _run_deliberation(thesis, agents, committee)
            profile = diagnose_competencies(thesis, _generate)
            extras["competency_profile"] = profile
            extras["committee"] = [a["name"] for a in agents]
            extras["deliberation_log"] = deliberation_log
            plan = development_plan(profile, deliberation_log, _generate)
            extras["development_plan"] = plan
            synthesis = committee.generate(
                "Synthesize the following committee reviews into one short feedback paragraph.\n\n" + deliberation_log,
                system_prompt="Output 3-5 sentences of consolidated feedback.",
                max_new_tokens=300,
            )
            return synthesis, extras

        # prescribed_committee
        profile = diagnose_competencies(thesis, _generate)
        agents = committee.assemble_committee(profile)
        deliberation_log = _run_deliberation(thesis, agents, committee)
        consolidated = committee.committee_deliberation(thesis, agents)
        plan = development_plan(profile, consolidated, _generate)
        extras["competency_profile"] = profile
        extras["committee"] = [a["name"] for a in agents]
        extras["deliberation_log"] = deliberation_log
        extras["development_plan"] = plan
        return consolidated, extras

    def _run_deliberation(thesis: str, agents: list, comm: CommitteeLoader) -> str:
        parts = []
        for a in agents:
            rev = comm.generate(
                f"Review this thesis and give brief feedback. Thesis: {thesis[:600]}",
                system_prompt=a["system_prompt"],
                max_new_tokens=200,
            )
            parts.append(f"[{a['name']}]: {rev}")
        return "\n\n".join(parts)

    def student_revision(thesis: str, feedback: str, d: dict) -> str:
        profile_spec = STUDENT_PROFILES.get(d.get("student_profile", ""), {})
        revision_style = profile_spec.get("revision_style", "engage")
        weak_dims = d.get("weak_dims", [])
        if revision_style == "copy_paste":
            prompt = (
                f"Revise this thesis by incorporating the feedback suggestions directly into the text, "
                f"making minimal structural changes. Integrate the suggestions verbatim where possible. "
                f"Thesis: {thesis[:300]}\nFeedback: {feedback[:350]}"
            )
        else:
            focus = f" Pay particular attention to: {', '.join(weak_dims)}." if weak_dims else ""
            prompt = (
                f"Revise this thesis incorporating the feedback. Consider the critique and address it substantively.{focus} "
                f"Thesis: {thesis[:300]}\nFeedback: {feedback[:350]}"
            )
        return committee.generate(prompt, max_new_tokens=200)

    def pure_llm_baseline(thesis: str) -> str:
        return committee.generate(
            f"Revise this thesis abstract to improve it. {thesis[:400]}",
            max_new_tokens=200,
        )

    results = []
    for d in doubles:
        feedback, extras = get_feedback_and_extras(d)
        rev = student_revision(d["thesis"], feedback, d)
        base = pure_llm_baseline(d["thesis"])

        emb_rev = embed_loader.get_embeddings([rev])[0]
        emb_base = embed_loader.get_embeddings([base])[0]
        mr = mechanical_reliance(emb_rev, emb_base, embed_loader.cosine_sim)
        trust = trust_rating(rev, committee.generate)
        quality = quality_rating(rev, committee.generate)
        spec = feedback_specificity(feedback, committee.generate)

        row = {
            "condition": d["condition"],
            "student_profile": d.get("student_profile", ""),
            "mechanical_reliance": float(mr),
            "trust": trust,
            "quality": quality,
            "feedback_specificity": spec,
            "thesis": d["thesis"][:500],
            "feedback": feedback[:800],
            "revision": rev[:800],
        }
        if extras.get("competency_profile"):
            row["competency_profile"] = extras["competency_profile"]
        if extras.get("committee"):
            row["committee"] = extras["committee"]
        if extras.get("deliberation_log"):
            row["deliberation_log"] = extras["deliberation_log"]
        if extras.get("development_plan"):
            plan = extras["development_plan"]
            row["development_plan"] = plan
            row["plan_quality"] = development_plan_quality(plan, lambda p, s, m: committee.generate(p, s, m))
            row["deliberation_metrics"] = societies_of_thought_metrics(extras.get("deliberation_log", ""))
        results.append(row)

    PILOT_RESULTS_PATH.write_text(json.dumps({"results": results}, indent=2), encoding="utf-8")

    sample_size = min(10, len(results))
    qualitative = [
        {"condition": r["condition"], "thesis": r["thesis"], "feedback": r["feedback"], "revision": r["revision"]}
        for r in results[:sample_size]
    ]
    QUALITATIVE_SAMPLES_PATH.write_text(json.dumps({"samples": qualitative}, indent=2), encoding="utf-8")

    if save_figures:
        import numpy as np
        import matplotlib.pyplot as plt

        from ..config import DOCS_VALIDATION_OUTPUTS

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

        # Plan quality by condition (only for C2/C3 which have plans)
        plan_results = [r for r in results if "plan_quality" in r]
        if plan_results:
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            conds_with_plans = [c for c in CONDITIONS if c != "single_agent"]
            for i, cond in enumerate(conds_with_plans):
                sub = [r for r in plan_results if r["condition"] == cond]
                if sub:
                    pq = [r["plan_quality"] for r in sub]
                    mean_pq = np.mean([(p.get("specificity", 3) + p.get("actionability", 3) + p.get("developmental_framing", 3)) / 3 for p in pq])
                    ax2.bar(i, mean_pq, label=cond, alpha=0.8)
            ax2.set_xticks(range(len(conds_with_plans)))
            ax2.set_xticklabels([c.replace("_", "\n") for c in conds_with_plans])
            ax2.set_ylabel("Mean plan quality (1-5)")
            ax2.set_title("Development plan quality by condition")
            plt.tight_layout()
            fig2.savefig(DOCS_VALIDATION_OUTPUTS / "plan_quality_by_condition.png", dpi=150)
            plt.close()

        # Feedback specificity by condition
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        for i, cond in enumerate(CONDITIONS):
            sub = [r for r in results if r["condition"] == cond]
            if sub:
                ax3.bar(i, np.mean([r.get("feedback_specificity", 3) for r in sub]), label=cond, alpha=0.8)
        ax3.set_xticks(range(len(CONDITIONS)))
        ax3.set_xticklabels([c.replace("_", "\n") for c in CONDITIONS])
        ax3.set_ylabel("Mean feedback specificity (1-5)")
        ax3.set_title("Feedback specificity by condition")
        plt.tight_layout()
        fig3.savefig(DOCS_VALIDATION_OUTPUTS / "feedback_specificity_by_condition.png", dpi=150)
        plt.close()

    return results
