# Presentation Narrative and Figure Mappings

Slide-by-slide narrative and figure references for the 5-minute presentation (23 slides).

**Speaking script:** See [SCRIPT.md](SCRIPT.md) for a TED-talk style lighting script aligned to all slides.

---

## Figure Reference (docs/validation_outputs/)

| Figure | Use |
|--------|-----|
| radar_by_model.png | Diagnostician: 0.5B vs 1.5B vs 7B mean profile |
| radar_by_cluster.png | Diagnostician: profiles by thesis cluster |
| radar_thesis_*.png | Diagnostician: per-thesis overlay (pick 1–2) |
| committee_assembly_demo.png | Committee: profile → committee mapping |
| feedback_comparison_thesis_*.png | C1 vs C3 side-by-side |
| deliberation_thesis_*.png | Committee deliberation excerpt |
| deliberation_thesis_*.txt | Raw deliberation text for quotes |
| development_plan_example.png | Gap map, exercises, trajectory |
| plan_quality_by_condition.png | Pilot: plan quality by condition |
| feedback_specificity_by_condition.png | Pilot: feedback specificity |
| github_improvement_heatmap.png | GitHub: author × dimension improvement |
| github_memo_validation.png | GitHub: overall validation summary |

---

## Slides 1–4: Problem and Question

**1. Title** — It's the Student, Not the Thesis: Personalized Adversarial Committees for Competency Development

**2. Problem** — We want to develop the researcher, not just polish the thesis; reduce mechanical AI use.
- *Talking point:* Generic AI feedback can reinforce surface-level editing instead of substantive competency growth.

**3. Problem (cont.)** — Generic feedback may not target a student's weakest dimensions.
- *Talking point:* A thesis weak on methodology may get feedback spread evenly across dimensions, missing the main gap.

**4. Research question** — Do personalized committees (matched to diagnosis) improve development plans and engagement?
- *Talking point:* We compare three conditions to test whether targeted committee feedback outperforms generic or random advice.

---

## Slides 5–11: Design and Method

**5. Design: three conditions** — Single agent / Random committee / Prescribed committee.
- *Talking point:* C1 = baseline; C2 = committee but no diagnosis; C3 = diagnosis drives committee assembly.

**6. Design: diagnostician** — Six dimensions (argument, evidence, methodology, theory, self-reflexivity, receptivity); scores 1–5 + justifications.
- **Figure:** `radar_by_model.png` — "We compared 0.5B, 1.5B, and 7B Qwen models; larger models produce more differentiated profiles."
- **Figure:** `radar_by_cluster.png` — "Profiles vary by thesis type (embedding cluster)."
- **Figure:** `radar_thesis_13058.png` (example) — Per-thesis overlay across models.

**7. Design: committee** — Five personas; prescribe 3 by lowest dimensions or pick random 3.
- **Figure:** `committee_assembly_demo.png` — "Different profiles trigger different committees. Low methodological scores → Methodologist joins the committee."

**8. Design: digital doubles** — Thesis, condition, student_profile, weak_dims, methodology from MACSS corpus.

**9. Design: development plan** — Gap map, exercises, trajectory from profile + deliberation feedback.
- **Figure:** `development_plan_example.png` — Shows gap map, exercises, and trajectory for one thesis.

**10. Design: metrics** — Mechanical reliance, trust, quality, plan quality, deliberation metrics.

**11. Method summary** — Pipeline: load corpus → build doubles → run condition (C1/C2/C3) → compute metrics.

---

## Slides 12–16: Results

**12. Results: pilot** — Mean mechanical reliance by condition (chart).
- **Figure:** `plan_quality_by_condition.png`, `feedback_specificity_by_condition.png`
- *Talking point:* Prescribed committee yields higher plan quality and more specific feedback than random or single agent.

**13. Results: pilot** — Mean trust by condition (chart).
- **Figure:** Same pilot figures; or reference qualitative_samples for trust/engagement evidence.

**14. Results: table** — MR, trust, quality, plan quality by condition (sample sizes).
- **Data:** Extract from `data/pilot_results.json` or docs.

**15. Qualitative** — Feedback–revision pairs and development plans in pilot_results / qualitative_samples.
- **Figure:** `feedback_comparison_thesis_13058.png` — Side-by-side C1 vs C3 feedback.
- **Figure:** `deliberation_thesis_13058.png` — Committee deliberation excerpt.
- **Text:** `deliberation_thesis_13058.txt` — Raw deliberation for quotes.
- *Talking point:* C3 feedback is dimension-targeted; C1 is generic.

**16. Interpretation** — Prescribed committee vs. random/single: effect on plan quality and engagement.
- **Figure:** `plan_quality_by_condition.png` — Pilot evidence.
- **Figure:** `github_improvement_heatmap.png` — "Week 2→9 improvement on plan dimensions; authors with development plans show gains."
- **Figure:** `github_memo_validation.png` — Overall GitHub retrospective summary.

---

## Slides 17–19: Limitations, Future, Data Process

**17. Limitations & future work** — Simulated students; small N; single LLM. Future: scale N; human subjects; Safe to Be Challenged (visible harmlessness label) as follow-up.

**18. Data: pilot & digital doubles** — MACSS thesis corpus → embedding clusters (KMeans) → sampled theses; 3 conditions × n per condition; ground-truth weak_dims for diagnostic accuracy. *For experimenters:* stratified sampling by cluster ensures variation across thesis types (not only computational vs qualitative).

**19. Data: GitHub retrospective** — 345 memo comments, 49 authors, 8 weeks (2–9), 17 authors with both Week 2 & 9. Retrospective pipeline: diagnose Week 2 → generate hypothetical plan → judge Week 9 on plan targets. Ecological validation only—students never received plans. *Key stat:* mean improvement 3.2–4.2 by dimension; heatmap shows per-author variation.

---

## Slides 20–22: Summary, Q&A, Reproducibility

**20. Summary** — It's the student, not the thesis; personalized committees + development plans; pilot + GitHub ecological validation; pipeline in place.

**21. Thank you / Q&A** — Contact / repo / report.md.

**22. Reproducibility** — `memo_w9_integration.ipynb` on Colab: clone from GitHub, enable GPU (T4/A100), run cells, download `colab_results.zip` before session ends. Integrates MACSS corpus, Qwen models, OpenAI (GitHub validation), and all seven results.
