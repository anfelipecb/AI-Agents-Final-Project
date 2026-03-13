# It's the Student, Not the Thesis: Personalized Adversarial Committees for Competency Development

**Figure 1.** *Conceptual diagram: student receives feedback from a committee of agents matched to their weakest competency dimensions; a development plan is produced from diagnosis and deliberation.*

---

## Motivation

Improving the *researcher* matters more than polishing the *thesis* artifact. When students use AI for feedback, we want to reduce mechanical reliance (copy-paste, surface edits) and increase substantive engagement with critique. This project asks: do **personalized adversarial committees**—assembled to target a student’s weakest competency dimensions—produce better development plans and engagement than a single generic agent or a random committee?

We frame the problem as competency development: a six-dimension diagnostician assesses the thesis, a committee (either prescribed by diagnosis or chosen at random) deliberates, and a development plan (gap map, exercises, trajectory) is generated. We compare three conditions: single agent, random committee, and prescribed committee.

**Figure 2.** *Motivation: from “generic feedback” to “personalized committee + development plan”; focus on competency dimensions rather than harmlessness visibility.*

---

## Method

### Three Conditions

1. **Single agent (C1)** — One helpful reviewer gives generic feedback. No diagnosis, no development plan.
2. **Random committee (C2)** — Three agents chosen at random deliberate; diagnosis and development plan are still produced for comparison.
3. **Prescribed committee (C3)** — Diagnose competencies → assemble committee from the three dimensions with lowest scores → deliberate → produce development plan.

**Figure 3.** *Flow: C1 = thesis → single review → feedback. C2/C3 = thesis → (diagnose) → committee deliberation → consolidated feedback → development plan.*

### Six-Dimension Diagnostician

Competency dimensions: argument_construction, evidence_evaluation, methodological_reasoning, theoretical_integration, self_reflexivity, receptivity_to_critique. The diagnostician returns scores (1–5) and justifications per dimension. The prescribed committee selects three agent personas (Methodologist, Theorist, Devil's Advocate, Encourager, Clarity Coach) whose “covered” dimensions match the three lowest scores.

### Digital Doubles and Student Profiles

Doubles are built with: thesis (from MACSS corpus), condition, **student_profile** (passive_accepter, methods_weak, descriptive_reporter), **weak_dims** (ground-truth weak dimensions for validation), and methodology.

### Data and Models

- **Data:** MACSS theses, abstracts for steering, GitHub memos (optional longitudinal).
- **Models:** Committee LLM (Qwen2.5-7B), diagnostician, development plan generator, embeddings, safety monitor (design feature only).

### Metrics

- **Mechanical reliance** — Cosine similarity between revision and generic baseline.
- **Trust (engagement)** — LLM rates engagement with feedback (1–5).
- **Quality** — LLM rates revision quality (1–5).
- **Plan quality** — Specificity, actionability, developmental_framing (1–5 each).
- **Deliberation metrics** — Perspective shifts, challenges, reconciliations (stub/regex).

**Future work: Safe to Be Challenged** — Visible harmlessness label as a trust intervention remains a design feature and can be tested in a follow-up study.

---

## Results

Pilot results are saved to `data/pilot_results.json` and figures to `figures/pilot_results.png`. Each result row can include competency_profile, committee, deliberation_log, development_plan, plan_quality, and deliberation_metrics for C2/C3.

---

## Summary

*It's the Student, Not the Thesis* reframes the project around competency development: personalized committees, a six-dimension diagnostician, and development plans. The harmlessness monitor is kept as a design feature; the main experiment compares single agent, random committee, and prescribed committee.
