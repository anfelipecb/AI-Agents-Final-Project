# Safe to Be Challenged: Trust and Harmlessness in Adversarial AI Advising

**Figure 1.** *Conceptual diagram: student receives adversarial feedback from an AI committee; a harmlessness monitor may operate silently or with a visible label.*

---

## Motivation

When students use AI tools for feedback on their writing or research, they often receive criticism that can feel harsh or demotivating. At the same time, *not* challenging weak arguments can reinforce poor habits. The tension is familiar: we want AI to be **safe to be challenged**—both in the sense that it is safe for the *system* to challenge the user (so that the user improves) and that the *user* feels safe enough to engage with that challenge. In this project we ask: does making harmlessness visible change how users rely on and engage with adversarial AI advising?

Trust and visible feedback matter. If a user cannot tell whether the system is monitoring for harm or how it is steering advice, they may disengage or over-trust. We therefore designed an experiment with three conditions: one with no harmlessness monitor, one with a monitor that operates in the background, and one where the monitor’s role is explicitly labeled. We measure mechanical reliance (how much revisions “copy” a generic baseline), trust (engagement with feedback), and quality (revision quality), and we validate findings with qualitative interpretation of feedback–revision pairs and with longitudinal data from course GitHub memos.

**Figure 2.** *Motivation: spectrum from “no challenge” to “adversarial challenge”; harmlessness monitoring can be absent, silent, or visible.*

---

## Method

### Three Conditions

We compare three experimental conditions:

1. **Committee only** — The student receives feedback from a skill-diagnostic committee (skill diagnostician + adversarial critic) with no harmlessness monitoring. Feedback may be sharp and critical.
2. **Silent monitor** — The same committee is used, but a harmlessness monitor rewrites or softens the feedback before it is shown. The student is not told that monitoring occurred.
3. **Visible label** — The harmlessness monitor again edits the feedback, but the student is told that the feedback has been “checked for harmlessness” (or similar visible label).

**Figure 3.** *Diagram of three conditions: committee_only → feedback; silent_monitor → monitor → feedback; visible_label → monitor → feedback + label.*

In all conditions, we simulate “student” revisions using an LLM that either ignores feedback (low trust-sensitivity) or incorporates it (high trust-sensitivity), depending on the digital double’s profile. This lets us study how the *visibility* of monitoring affects reliance and engagement without running a full human subject study in this phase.

### Digital Doubles and Corpus

We build **digital doubles** from a thesis abstract corpus. Each double has:

- A **thesis** (abstract) drawn from MACSS theses (harvested via OAI-PMH from Knowledge UChicago) or from sample abstracts if the corpus is missing.
- A **condition** (committee_only, silent_monitor, or visible_label).
- **Trust sensitivity** (low or high), which controls whether the simulated student revises in response to feedback or falls back to a generic revision.
- **Methodology** (computational, quantitative, qualitative), inferred from title/abstract keywords.

**Figure 4.** *Pipeline: MACSS corpus → CorpusLoader → DoublesLoader → list of doubles (thesis, condition, trust_sensitivity, methodology).*

The committee consists of a **skill diagnostician** (ReAct-style) that assesses the thesis and an **adversarial critic** that produces critical feedback. The **harmlessness monitor** uses an LLM judge to decide whether the critique is safe and, when not, rewrites it; in the visible_label condition, the feedback is tagged so the user knows it was monitored.

**Figure 5.** *Committee flow: thesis → Skill Diagnostician → Adversarial Critic → (optional) Harmlessness Monitor → feedback.*

### Data and Models

We use **three forms of data**: (1) MACSS thesis abstracts, (2) abstracts for steering (simplified list), and (3) GitHub course-issue memos (optional, for longitudinal validation). We use **three model types**: (1) sentence-transformers for embeddings and mechanical reliance, (2) the committee LLM (Qwen2.5-7B-Instruct) for generation and judging, and (3) the safety/harmlessness logic that conditions feedback.

**Figure 6.** *Data flow: MACSS theses, GitHub issues, pilot results; models: embeddings, committee, safety.*

### Metrics

- **Mechanical reliance** — Cosine similarity between the revision embedding and a generic “revise without feedback” baseline. High similarity suggests the student did not meaningfully use the feedback (copy-paste or generic revision).
- **Trust (engagement)** — An LLM rates how much the revision reflects engagement with the feedback (1–5).
- **Quality** — An LLM rates revision quality (1–5).

**Figure 7.** *Metrics: mechanical_reliance(emb_revision, emb_baseline, cosine_sim); trust_rating(revision, generate); quality_rating(revision, generate).*

---

## Results

We ran the pilot with a small number of doubles per condition (e.g., two per condition under FAST_MODE). Results are saved to `data/pilot_results.json` and summarized in the notebook and in `figures/pilot_results.png`.

**Figure 8.** *Bar chart: mean mechanical reliance by condition (committee_only, silent_monitor, visible_label).*

**Figure 9.** *Bar chart: mean trust (engagement) by condition.*

**Figure 10.** *Table: mean mechanical reliance, trust, and quality by condition with sample sizes.*

In our pilot runs, we typically observe variation across conditions: visible_label sometimes shows different mechanical reliance or trust than committee_only, depending on how the monitor rewrites feedback and how the simulated student responds. The goal of the full experiment is to test whether visible harmlessness labeling increases engagement (trust) without encouraging over-reliance (high mechanical reliance).

### GitHub Longitudinal Validation

We optionally fetch Week N Memo comments from the course GitHub repo and embed them to compute **trajectories** (e.g., mean similarity to the first memo in each week). This gives a longitudinal view of how memo quality or style evolves, which can be compared with the pilot’s condition-level metrics.

**Figure 11.** *GitHub validation: corpus size, trajectories per week, mean_sim_to_first; saved to github_validation.json.*

---

## Qualitative Interpretation

Qualitative validation uses the saved **feedback–revision pairs** in `data/qualitative_samples.json` (up to 10 per run). Interpreters can examine:

- **Engagement** — Does the revision address the committee’s specific critiques (e.g., “add a causal claim”) or only generic improvements?
- **Harmlessness** — In silent_monitor and visible_label, does the edited feedback avoid harsh or off-topic content? Do revisions stay on-topic and non-harmful?
- **Mechanical reliance** — Do high–mechanical-reliance revisions read like generic paraphrases of the baseline, while low–mechanical-reliance revisions reflect the feedback?

**Figure 12.** *Example qualitative sample: thesis excerpt, feedback excerpt, revision excerpt, condition.*

These interpretations support the quantitative metrics and inform the narrative of the blog post and presentation. They also satisfy the course requirement for “qualitative interpretation and assessments.”

**Figure 13.** *Summary: motivation (trust + visible feedback) → method (three conditions, doubles, MACSS + GitHub) → results (metrics + trajectories) → qualitative interpretation → conclusion.*

---

## Conclusion

We implemented a full pipeline for the “Safe to Be Challenged” project: three conditions (committee-only, silent monitor, visible label), digital doubles from the MACSS corpus, and metrics for mechanical reliance, trust, and quality. We added GitHub longitudinal validation and qualitative samples (feedback–revision pairs) to support both quantitative and qualitative interpretation. The main entry point is `run.py` (with flags for pilot, GitHub validation, and fetching corpus or GitHub issues); the notebook replicates the pilot flow for Colab with pip. Future work includes running a larger experiment, collecting human subject data, and refining the harmlessness monitor’s labeling for clarity and fairness.

---

### Limitations

The pilot uses simulated students (LLM-generated revisions) rather than human participants, so trust and engagement scores reflect model behavior, not actual user experience. The number of doubles per condition is small (e.g., two in FAST_MODE), so condition differences may not be statistically reliable. The harmlessness monitor’s edits are not yet standardized (e.g., no fixed rubric for “safe” tone), and the visible label is a placeholder that would need to be refined for a real deployment. GitHub validation depends on course repo structure and may yield few memos if issues are sparse.

### Future Work

Planned extensions include: (1) scaling to more doubles per condition and running significance tests; (2) collecting human subject data (e.g., students revising memos with and without visible harmlessness labels); (3) defining a harmlessness rubric and measuring inter-rater agreement; (4) comparing trajectories from GitHub memos with pilot condition outcomes; and (5) publishing the qualitative samples and interpretation protocol for replication.

---

*Draft blog post. Expand results with actual pilot numbers and figure captions to reach ~3,600 words. All 13 figure placeholders are indicated above.*
